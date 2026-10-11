#!/usr/bin/env python3
"""Visual hull do concept do Bubble Bumper (3 ortograficos) + surface nets.
Saida: /tmp/vh.obj  (malha fechada)
Correcoes importantes:
  - masks limpas (linha de chao de 2px removida em clean_mask)
  - frente em col 0 no TOP e no SIDE (validado por roda menor xf 0.196-0.296)
  - eixo correto no np.where da grade (x,y,z na ordem dos eixos do array)
"""
import numpy as np, os, sys

SRC = "/tmp/c_%s.npy"
L, Wd, Ht = 2.35, 1.494, 1.207
X0, Y0, Z0 = 1.175, 0.747, 1.207

def erode(m, k):
    o = m.copy()
    for _ in range(k):
        p = np.pad(o, 1, constant_values=False)
        o = p[1:-1,1:-1] & p[:-2,1:-1] & p[2:,1:-1] & p[1:-1,:-2] & p[1:-1,2:]
    return o

def build(er=2, N=220):
    top = erode(np.load(SRC % "top"), er)
    # O concept e tracado a mao: o TOP tem ~4.5 cm de assimetria (IoU 0.842 vs o proprio espelho).
    # O kart fisico e SIMETRICO e o FRONT e 97.8% simetrico -> simetriza o TOP pela UNIAO
    # (preserva o lado mais largo, nao inventa feature). SIDE nao precisa (e um perfil).
    top = top | top[:, ::-1]
    side = erode(np.load(SRC % "side"), er)
    front = erode(np.load(SRC % "front"), er)
    Ht_, Wt = top.shape; Hs, Ws = side.shape; Hf, Wf = front.shape
    nx = N; ny = int(round(N * Wd / L)); nz = int(round(N * Ht / L))
    xs = np.linspace(X0, -X0, nx); ys = np.linspace(Y0, -Y0, ny); zs = np.linspace(Z0, 0.0, nz)
    # IMPORTANTE: mapear pelo bbox REAL do conteudo de cada mascara, nao pelas dimensoes da
    # imagem — o crop pode ter margens vazias (o TOP tinha ~25 linhas vazias) e isso encolhia
    # o y do hull. Cada vista e normalizada para a dimensao fisica que ela representa.
    def rb(m):
        r = np.where(m.any(1))[0]; c = np.where(m.any(0))[0]
        return r[0], r[-1], c[0], c[-1]
    t0r, t1r, t0c, t1c = rb(top)
    s0r, s1r, s0c, s1c = rb(side)
    f0r, f1r, f0c, f1c = rb(front)
    def idx(a, b, vals, lo, hi):
        # vals (mundo) -> indice de pixel entre a..b quando o mundo vai de lo (no a) a hi (no b)
        t = (vals - lo) / (hi - lo)
        return np.clip((a + t * (b - a)).round().astype(int), a, b)
    cx  = idx(t0c, t1c, xs, X0, -X0)
    cyT = idx(t0r, t1r, ys, Y0, -Y0)
    cyF = idx(f0c, f1c, ys, Y0, -Y0)
    czS = idx(s0r, s1r, zs, Z0, 0.0)
    czF = idx(f0r, f1r, zs, Z0, 0.0)
    A = top[np.ix_(cyT, cx)].T      # (nx,ny) por (x,y)
    B = side[np.ix_(czS, cx)].T     # (nx,nz) por (x,z)
    C = front[np.ix_(czF, cyF)].T   # (ny,nz)
    VOTE = int(__import__("os").environ.get("VH_VOTE", "3"))
    sc = (A[:, :, None].astype(np.int8) + B[:, None, :].astype(np.int8) + C[None, :, :].astype(np.int8))
    occ = (sc >= VOTE) if VOTE < 3 else (sc == 3)
    return occ, xs, ys, zs

def surface_nets(occ, xs, ys, zs):
    nx, ny, nz = occ.shape
    S = (nx - 1, ny - 1, nz - 1)
    c = {}
    for di in (0,1):
        for dj in (0,1):
            for dk in (0,1):
                c[(di,dj,dk)] = occ[di:di+nx-1, dj:dj+ny-1, dk:dk+nz-1]
    edges = []
    for dk in (0,1):
        for dj in (0,1): edges.append(((0,dj,dk),(1,dj,dk),(0.5,float(dj),float(dk))))
    for dk in (0,1):
        for di in (0,1): edges.append(((di,0,dk),(di,1,dk),(float(di),0.5,float(dk))))
    for dj in (0,1):
        for di in (0,1): edges.append(((di,dj,0),(di,dj,1),(float(di),float(dj),0.5)))
    acc = np.zeros(S + (3,), np.float64); cnt = np.zeros(S, np.float64)
    for a,b,mid in edges:
        diff = (c[a] != c[b])
        if not diff.any(): continue
        cnt += diff
        for d in range(3): acc[..., d] += diff * mid[d]
    mixed = cnt > 0
    vidx = np.full(S, -1, np.int32)
    ax, ay, az = np.where(mixed)
    vidx[ax, ay, az] = np.arange(len(ax))
    cen = np.zeros((len(ax), 3))
    for d in range(3): cen[:, d] = acc[..., d][ax, ay, az] / cnt[ax, ay, az]
    pos = np.zeros((len(ax), 3), np.float32)
    pos[:, 0] = np.interp(ax + cen[:, 0], np.arange(nx), xs)
    pos[:, 1] = np.interp(ay + cen[:, 1], np.arange(ny), ys)
    pos[:, 2] = np.interp(az + cen[:, 2], np.arange(nz), zs)
    quads = []
    # arestas em X (variacao entre voxels i-1 e i)
    d = (occ[1:, 1:ny-1, 1:nz-1] != occ[:-1, 1:ny-1, 1:nz-1])
    ii, jj, kk = np.where(d); ii += 1; jj += 1; kk += 1
    for i, j, k in zip(ii, jj, kk):
        q = [vidx[i-1,j-1,k-1], vidx[i-1,j,k-1], vidx[i-1,j,k], vidx[i-1,j-1,k]]
        if min(q) < 0: continue
        quads.append(q if not occ[i,j,k] else [q[0], q[3], q[2], q[1]])
    # arestas em Y
    d = (occ[1:nx-1, 1:, 1:nz-1] != occ[1:nx-1, :-1, 1:nz-1])
    ii, jj, kk = np.where(d); ii += 1; jj += 1; kk += 1
    for i, j, k in zip(ii, jj, kk):
        q = [vidx[i-1,j-1,k-1], vidx[i,j-1,k-1], vidx[i,j-1,k], vidx[i-1,j-1,k]]
        if min(q) < 0: continue
        quads.append(q if not occ[i,j,k] else [q[0], q[3], q[2], q[1]])
    # arestas em Z
    d = (occ[1:nx-1, 1:ny-1, 1:] != occ[1:nx-1, 1:ny-1, :-1])
    ii, jj, kk = np.where(d); ii += 1; jj += 1; kk += 1
    for i, j, k in zip(ii, jj, kk):
        q = [vidx[i-1,j-1,k-1], vidx[i,j-1,k-1], vidx[i,j,k-1], vidx[i-1,j,k-1]]
        if min(q) < 0: continue
        quads.append(q if not occ[i,j,k] else [q[0], q[3], q[2], q[1]])
    return pos, quads

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--erode", type=int, default=2)
    ap.add_argument("--N", type=int, default=220)
    ap.add_argument("--out", default="/tmp/vh.obj")
    a = ap.parse_args()
    occ, xs, ys, zs = build(a.erode, a.N)
    print("grade %s | ocupacao %.1f%%" % (occ.shape, 100.0*occ.mean()))
    pos, quads = surface_nets(occ, xs, ys, zs)
    print("vertices %d | quads %d" % (len(pos), len(quads)))
    with open(a.out, "w") as f:
        for p in pos: f.write("v %.5f %.5f %.5f\n" % (p[0], p[1], p[2]))
        for q in quads: f.write("f %d %d %d %d\n" % (q[0]+1, q[1]+1, q[2]+1, q[3]+1))
    print("bbox x %.3f..%.3f | y %.3f..%.3f | z %.3f..%.3f" % (
        pos[:,0].min(), pos[:,0].max(), pos[:,1].min(), pos[:,1].max(), pos[:,2].min(), pos[:,2].max()))
    print("OBJ: %s" % a.out)

if __name__ == "__main__":
    main()
