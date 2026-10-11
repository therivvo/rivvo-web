#!/usr/bin/env python3
import sys, os, json
MD=os.path.dirname(os.path.abspath(__file__))
S=os.path.join(MD,"REBUILD-STATE.json")
st={}
if os.path.exists(S): st=json.load(open(S))
k=sys.argv[1] if len(sys.argv)>1 else ""
v=st.get(k,0)
print("%s=%s"%(k,v))
sys.exit(0 if float(v or 0)>0 else 1)
