import base64, importlib.util, io, json, zipfile, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('visibility_bot',Path(__file__).resolve().parents[1]/'scripts/community-registry-telegram-bot.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class VisibilityTests(unittest.TestCase):
 def entry(self):return {'id':'vpn','version':'1.1.2','name':'VPN','status':'pending','source':'https://github.com/test/vpn/releases/download/v1/vpn.zip'}
 def test_only_identical_merged_entry_is_activated(self):
  e=self.entry();payload={'plugins':[e]};response={'sha':'original','content':base64.b64encode(json.dumps(payload).encode()).decode()}
  rejected={'number':1,'base':{'ref':'main'},'merged_at':None};merged={'number':2,'base':{'ref':'main'},'merged_at':'date'}
  with patch.object(b,'github',side_effect=[response,[rejected,merged],{}]) as gh,patch.object(b,'changed_plugins',return_value=([dict(e,_change='added',_removed=False)],None)) as changes,patch.object(b,'validate_archive') as validate:
   b.reconcile_merged_listings({});changes.assert_called_once_with(merged);validate.assert_called_once_with(e)
   args=gh.call_args.args;self.assertEqual(args[1],'PUT');self.assertEqual(args[2]['sha'],'original')
   saved=json.loads(base64.b64decode(args[2]['content']));self.assertEqual(saved['plugins'][0]['status'],'approved')
 def test_old_version_cannot_approve_new_pending_version(self):
  e=self.entry();response={'sha':'x','content':base64.b64encode(json.dumps({'plugins':[e]}).encode()).decode()}
  pr={'merged_at':'date','base':{'ref':'main'}}
  with patch.object(b,'github',side_effect=[response,[pr]]) as gh,patch.object(b,'changed_plugins',return_value=([dict(e,version='1.0.0')],None)),patch.object(b,'validate_archive') as validate:
   b.reconcile_merged_listings({});validate.assert_not_called();self.assertEqual(gh.call_count,2)
 def test_invalid_archive_stays_pending(self):
  e=self.entry();response={'sha':'x','content':base64.b64encode(json.dumps({'plugins':[e]}).encode()).decode()}
  with patch.object(b,'github',side_effect=[response,[{'merged_at':'date','base':{'ref':'main'}}]]) as gh,patch.object(b,'changed_plugins',return_value=([e],None)),patch.object(b,'validate_archive',side_effect=RuntimeError('bad ZIP')):
   b.reconcile_merged_listings({});self.assertEqual(gh.call_count,2)
 def test_localized_names(self):
  for name,valid in [({'ru':'VPN','en':'VPN'},True),('VPN',True),({},False),({'ru':''},False),({'ru':12},False)]:
   data=io.BytesIO()
   with zipfile.ZipFile(data,'w') as z:z.writestr('manifest.json',json.dumps({'id':'vpn','version':'1.1.2','name':name}))
   stream=io.BytesIO(data.getvalue());stream.geturl=lambda: 'https://github.com/test/vpn.zip'
   with patch.object(b.urllib.request,'urlopen',return_value=stream):
    if valid:b.validate_archive(self.entry())
    else:
     with self.assertRaises(RuntimeError):b.validate_archive(self.entry())
if __name__=='__main__':unittest.main()
