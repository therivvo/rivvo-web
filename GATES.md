- [x] R125-1: Inspeção do estado atual e contrato técnico identifica a causa estrutural e preserva R124.
  EVIDENCE: `assets/hero-kart-v2/R124/hero-kart-v2-R124.blend` preservado; gerador canônico contém UV por mesh, remapeamento de material por LOD, caps triangulados e correção final de normais.
- [x] R125-2: Correção estrutural única aplicada no gerador autoral, sem empilhar primitivas cosméticas.
  EVIDENCE: build real gerou `assets/hero-kart-v2/R125/hero-kart-v2-R125.blend` (808469 bytes); mudança promoveu pipeline autoral R124 ao gerador canônico.
- [x] R125-3: Blender 4.0.2 no GPU runner LXC105 produz beauty/profile/top/rear/clearance do mesmo R125.
  EVIDENCE: cinco PNGs não vazios em `assets/hero-kart-v2/R125/renders/`; runner output confirmou `Blender 4.0.2`, `R125_RENDER_SET_OK`.
- [x] R125-4: Auditoria técnica do R125 executada e resultado registrado.
  EVIDENCE: `technical-audit.json`: LOD0 39832/5/0, LOD1 21098/4/0, LOD2 6028/3/0, COLLISION 36/0; `technical_pass=true`.
- [x] R125-5: Primary vision analisou exatamente os cinco renders do R125.
  EVIDENCE: `visual-qa.md` registra análise individual de beauty/profile/top/rear/clearance; resultado REJECT por shell tablet/bubble e piloto detached/mannequin.
- [x] R125-6: Sol gpt-5.6-sol xhigh somente se primary vision passar; caso contrário status explicitamente não chamado.
  EVIDENCE: primary vision REJECT; Sol NÃO INVOCADO por protocolo; export/runtime bloqueados.
- [x] R125-7: Documentação, vault, wiki e memória atualizados; commit atômico e push apenas dos arquivos escopados.
  EVIDENCE: docs/vault/wiki atualizados; commits `dc67628` e `f2982ef` publicados em `origin/main`; segundo commit removeu bytecode gerado e deixou somente GATES, gerador canônico, documentação e artefatos R125 escopados.

- [ ] R142-1: Gerador estrutural completo baseado no pipeline R139, com carroceria, cockpit, piloto integrado, rodas, traseira, LODs e COLLISION.
  CHECK: python3 -m py_compile R142_build.py R142_render.py
  EXPECT: exit code 0
- [ ] R142-2: Build remoto real no Blender 4.0.2 salva o blend R142 e não contém traceback.
- [ ] R142-3: Cinco renders R142 e technical-audit.json existem localmente; todos os gates técnicos passam.
- [ ] R142-4: Vision primário analisa as cinco vistas; Sol só é chamado se as cinco passarem.
- [ ] R142-5: Se aprovação dupla ocorrer, commit/push atômico e cinco imagens anexadas ao usuário; caso contrário, rejeição documentada e próxima revisão criada.

- [ ] R154-1: Reconstrução do piloto executada em R154 com blend, cinco renders e auditoria técnica válida.
  EVIDENCE: R154 build/render reais no Blender 4.0.2/LXC105; cinco PNGs e `technical-audit.json` localizados; `all_structural_gates_pass: true`.
- [ ] R154-2: Vision primário aprova as cinco vistas e Sol aprova a mesma revisão.
  EVIDENCE: R154 rejeitada visualmente nas cinco vistas; Sol não chamado para aprovação final.
