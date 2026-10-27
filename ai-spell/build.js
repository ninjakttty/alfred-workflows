const fs = require('node:fs')
const path = require('node:path')
const { execFileSync } = require('node:child_process')
const root = __dirname
const objects = []
const connections = {}
const uidata = {}
function object(uid, type, config, x, y, version = 1) {
  objects.push({ uid, type: 'alfred.workflow.' + type, config, version })
  uidata[uid] = { xpos: x, ypos: y }
}
function link(from, to, modifiers = 0, modifiersubtext = '') {
  ;(connections[from] ||= []).push({ destinationuid: to, modifiers, modifiersubtext, vitoclose: false })
}
object('spell', 'input.scriptfilter', {
  keyword: 'spell', argumenttype: 1, withspace: true, title: 'AI Spell',
  subtext: 'Check spelling with on-device Apple Intelligence', runningsubtext: 'Checking spelling…',
  script: 'exec ./ai-spell-native filter "$1"', type: 5, scriptargtype: 1, scriptfile: '', escaping: 102,
  alfredfiltersresults: false, argumenttreatemptyqueryasnil: false, argumenttrimmode: 0,
  queuedelaycustom: 2, queuedelaymode: 0, queuedelayimmediatelyinitially: true, queuemode: 1, runmodemode: 0,
}, 300, 50, 3)
object('selection', 'trigger.hotkey', {
  action: 1, argument: 1, argumenttext: 'spell ', hotkey: 1, hotmod: 1966080, hotstring: 'S',
  focusedappvariable: false, focusedappvariablename: '', leftcursor: false, modsmode: 0, relatedAppsMode: 0,
}, 20, 50, 2)
uidata.selection.note = 'Hyper+S shows Alfred immediately with the selected text. No startup script.'
object('external', 'trigger.external', { triggerid: 'spell', workflowid: 'net.ninjakitty.ai-spell', passinput: true, available: 0 }, 20, 230)
link('external', 'spell')
for (const [id, autopaste, modifiers, y] of [['paste', true, 0, 50], ['copy', false, 1048576, 230]]) {
  object('trace-' + id, 'action.script', { script: `exec ./ai-spell-native action ${id} "$1"`, type: 5, scriptargtype: 1, scriptfile: '', escaping: 102, concurrently: true }, 580, y, 2)
  object(id, 'output.clipboard', { clipboardtext: '{query}', autopaste, ignoredynamicplaceholders: true, transient: false }, 850, y, 3)
  link('spell', 'trace-' + id, modifiers, modifiers ? 'Copy correction to clipboard' : '')
  link('trace-' + id, id)
}
object('debug-keyword', 'input.keyword', { keyword: 'spell-debug', argumenttype: 2, withspace: false, text: 'Open AI Spell diagnostics', subtext: 'Open the metadata-only diagnostic log' }, 20, 430)
object('debug-open', 'action.script', {
  script: 'cache="${alfred_workflow_cache:-$HOME/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/net.ninjakitty.ai-spell}"\n/bin/mkdir -p "$cache"\n/usr/bin/touch "$cache/debug.jsonl"\n/bin/chmod 600 "$cache/debug.jsonl"\n/usr/bin/open -a TextEdit "$cache/debug.jsonl"',
  type: 5, scriptargtype: 1, scriptfile: '', escaping: 102, concurrently: false,
}, 300, 430, 2)
link('debug-keyword', 'debug-open')
const info = {
  name: 'AI Spell', bundleid: 'net.ninjakitty.ai-spell', createdby: 'Yuri Parsons',
  webaddress: 'https://www.ninjakitty.net', version: '2.0.0',
  description: 'Native on-device Apple Intelligence spelling suggestions and definitions.',
  category: 'Tools', disabled: false, objects, connections, uidata,
  readme: fs.readFileSync(path.join(root, 'README.md'), 'utf8'), variables: { debug_mode: '1' }, variablesdontexport: [],
}
function xml(value) {
  if (typeof value === 'boolean') return value ? '<true/>' : '<false/>'
  if (typeof value === 'number') return `<integer>${value}</integer>`
  if (typeof value === 'string') return '<string>' + escape(value) + '</string>'
  if (Array.isArray(value)) return '<array>' + value.map(xml).join('') + '</array>'
  return '<dict>' + Object.entries(value).map(([key, v]) => '<key>' + escape(key) + '</key>' + xml(v)).join('') + '</dict>'
}
function escape(value) { return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') }
fs.writeFileSync(path.join(root, 'info.plist'), '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">' + xml(info) + '</plist>\n')
const archive = path.join(root, 'ai-spell.alfredworkflow')
fs.rmSync(archive, { force: true })
execFileSync('/usr/bin/zip', ['-q', archive, 'info.plist', 'ai-spell-native', 'README.md', 'LICENSE', 'icon.png'], { cwd: root })
console.log('Built ai-spell.alfredworkflow')
