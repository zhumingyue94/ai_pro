import json, re, subprocess
from pathlib import Path
import yaml
root=Path(__file__).parent
mods=[]
for kind in ('app','pc'):
 text=(root/f'01_requirements/{kind}/模块拆分清单.md').read_text(encoding='utf-8')
 for line in text.splitlines():
  m=re.match(r'\|\s*(REQ-(?:APP|PC)-\d+)\s*\|\s*([^|]+?)\s*\|.*?ID=(\d+)',line)
  if m: mods.append({'kind':kind,'req':m.group(1),'name':m.group(2).strip(),'module':int(m.group(3))})
reg=json.loads((root/'module_case_map/module_case_map.json').read_text(encoding='utf-8'))['modules_by_req_id']
outdir=root/'06_zentao_sync/_mapping_check_20261012'; outdir.mkdir(exist_ok=True)
for m in mods:
 output=outdir/f"{m['req']}_module_{m['module']}.json"
 for attempt in range(3):
  p=subprocess.run(['python',str(root.parent.parent.parent/'scripts/fetch_zentao_module_cases.py'),'--product','1','--project','29','--module',str(m['module']),'--page-size','50','--format','json','--output',str(output)],capture_output=True,text=True,encoding='utf-8',errors='replace')
  if p.returncode==0 and output.exists(): break
 else: raise RuntimeError(f"{m['req']}: {p.stdout}{p.stderr}")
for m in mods:
 ypath=root/'04_testcases'/m['kind']/f"TC_{m['req']}.yaml"; y=yaml.safe_load(ypath.read_text(encoding='utf-8')); ycases={x['id']:x for x in y.get('cases',[])}
 rr=reg.get(m['req'],{}); rcases=rr.get('cases',{}); z=json.loads((outdir/f"{m['req']}_module_{m['module']}.json").read_text(encoding='utf-8')); zcases=z.get('cases',[]); zmap={int(x.get('case') or x.get('caseID') or x.get('id')):x for x in zcases}
 local_ids=set(ycases); reg_ids=set(rcases); regz={cid:rcases[cid].get('zentao_case_id') for cid in rcases}; zids=set(zmap); registered=[(cid,zid) for cid,zid in regz.items() if zid]; dup={zid:[cid for cid,x in regz.items() if x==zid] for zid in set(x for x in regz.values() if x) if list(regz.values()).count(zid)>1}; mapped_local=[cid for cid,zid in regz.items() if zid and int(zid) in zids]; missing_zentao=[(cid,regz.get(cid)) for cid in local_ids if cid not in rcases or not regz.get(cid) or int(regz[cid]) not in zids]
 m.update({'yaml':ypath,'ycases':ycases,'rcases':rcases,'z':z,'zmap':zmap,'local_only':sorted(local_ids-reg_ids),'registry_only':sorted(reg_ids-local_ids),'unmapped':sorted(missing_zentao),'missing_zentao_cases':sorted(zids-set(int(x) for x in regz.values() if x)),'wrong_module':[cid for cid,zid in regz.items() if zid and int(zid) not in zids],'duplicate':dup,'mapped_count':len(mapped_local)})
summary={'modules':len(mods),'yaml_cases':sum(len(m['ycases']) for m in mods),'zentao_cases':sum(len(m['zmap']) for m in mods),'registry_cases':sum(len(m['rcases']) for m in mods),'one_to_one_modules':sum(not (m['local_only'] or m['registry_only'] or m['unmapped'] or m['missing_zentao_cases'] or m['wrong_module'] or m['duplicate']) and len(m['ycases'])==len(m['zmap']) for m in mods)}
L=['# 全部 APP/PC 模块本地用例与禅道用例一对一映射检查','','- 检查时间：2026-10-12','- APP 模块 ID 来源：`01_requirements/app/模块拆分清单.md`','- PC 模块 ID 来源：`01_requirements/pc/模块拆分清单.md`','- 映射来源：`module_case_map/module_case_map.json`','- 本地用例来源：`04_testcases/app`、`04_testcases/pc`','- 禅道用例来源：通过 `scripts/fetch_zentao_module_cases.py` 实时拉取各模块，未读取 `06_zentao_sync` 历史同步文件','','## 总体汇总','','| 项目 | 数量 |','|---|---:|',f'| 模块总数 | {summary["modules"]} |',f'| 本地 YAML 用例 | {summary["yaml_cases"]} |',f'| 禅道实际用例 | {summary["zentao_cases"]} |',f'| 映射注册表用例 | {summary["registry_cases"]} |',f'| 完全一对一模块 | {summary["one_to_one_modules"]} |','','## 判定规则','', '模块满足以下条件时判定为一对一映射：本地 YAML 用例 ID 与注册表 case_id 集合一致；每条本地用例有且仅有一个有效 zentao_case_id；禅道 ID 不重复；映射 ID 均存在于对应禅道模块实际用例清单；禅道实际用例不存在未映射项。']
for m in mods:
 status='是' if not (m['local_only'] or m['registry_only'] or m['unmapped'] or m['missing_zentao_cases'] or m['wrong_module'] or m['duplicate']) and len(m['ycases'])==len(m['zmap']) else '否'
 L += ['',f'## {m["req"]}（{m["name"]}，禅道模块 `{m["module"]}`）','', '### 1. 本地用例清单', '', '| 本地用例 ID | 标题 | 映射禅道用例 ID | 注册状态 |','|---|---|---:|---|']
 for cid in sorted(m['ycases']):
  title=str(m['ycases'][cid].get('title','')).replace('|','\\|'); item=m['rcases'].get(cid,{})
  L.append(f'| `{cid}` | {title} | `{item.get("zentao_case_id") or "未建立"}` | {item.get("mapping_status") or "未进入映射表"} |')
 L += ['', '### 2. 禅道用例清单','', '| 禅道用例 ID | 标题 | 是否已映射 | 对应本地用例 |','|---:|---|---|---|']
 mapped_ids=[int(x['zentao_case_id']) for x in m['rcases'].values() if x.get('zentao_case_id')]
 for zid in sorted(m['zmap']):
  title=str(m['zmap'][zid].get('title','')).replace('|','\\|'); ids=', '.join('`'+cid+'`' for cid,x in m['rcases'].items() if x.get('zentao_case_id') and int(x['zentao_case_id'])==zid) or '未映射'
  L.append(f'| `{zid}` | {title} | {"是" if zid in mapped_ids else "否"} | {ids} |')
 L += ['', '### 3. 映射关系检查结果','', '| 检查项 | 结果 | 数量/说明 |','|---|---|---|',f'| 本地 YAML 用例数 | {len(m["ycases"])} | - |',f'| 禅道实际用例数 | {len(m["zmap"])} | - |',f'| 注册表用例数 | {len(m["rcases"])} | - |',f'| 是否一对一映射 | **{status}** | - |',f'| 仅存在于本地 YAML | {len(m["local_only"])} | {", ".join(m["local_only"]) or "无"} |',f'| 仅存在于映射注册表 | {len(m["registry_only"])} | {", ".join(m["registry_only"]) or "无"} |',f'| 未建立有效禅道映射 | {len(m["unmapped"])} | {", ".join(x[0] for x in m["unmapped"]) or "无"} |',f'| 禅道未被映射 | {len(m["missing_zentao_cases"])} | {", ".join(map(str,m["missing_zentao_cases"])) or "无"} |',f'| 映射到错误模块/不存在 ID | {len(m["wrong_module"])} | {", ".join(m["wrong_module"]) or "无"} |',f'| 重复使用禅道 ID | {len(m["duplicate"])} | {", ".join(str(k)+":"+",".join(v) for k,v in m["duplicate"].items()) or "无"} |']
(root/f'全部模块本地与禅道一对一映射检查_20261012.md').write_text('\n'.join(L)+'\n',encoding='utf-8'); print(json.dumps(summary,ensure_ascii=False))
