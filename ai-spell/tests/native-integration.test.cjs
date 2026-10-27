const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const os = require('node:os')
const { execFileSync } = require('node:child_process')
const { setTimeout: delay } = require('node:timers/promises')
const binary = path.resolve(__dirname, '../ai-spell-native')
function setup() {
  const cache = fs.mkdtempSync(path.join(os.tmpdir(), 'ai-spell-test-'))
  const env = { ...process.env, alfred_workflow_cache: cache, debug_mode: '1' }
  const filter = (query, id) => JSON.parse(execFileSync(binary, ['filter', query], { env: { ...env, ...(id ? { spell_request_id: id } : {}) } }))
  const state = id => JSON.parse(fs.readFileSync(path.join(cache, 'request-' + id, 'state.json')))
  return { cache, env, filter, state }
}

test('real model returns suggestions in the same polling session', { timeout: 90000 }, async () => {
  const { cache, filter, state } = setup()
  try {
    const started = Date.now()
    const initial = filter('heelo')
    console.log('Initial native loading feedback:', Date.now() - started, 'ms')
    assert.equal(initial.items[0].valid, false)
    assert.equal(initial.rerun, 0.25)
    const id = initial.variables.spell_request_id
    let response = initial
    for (let i = 0; i < 250 && response.rerun; i++) {
      await delay(200)
      response = filter('heelo', id)
      assert.equal(response.variables.spell_request_id, id)
    }
    assert.equal(state(id).status, 'ready', JSON.stringify(state(id)))
    assert.ok(response.items.some(row => row.arg.toLowerCase() === 'hello'))
    assert.ok(response.items.every(row => row.subtitle.length > 0))
    assert.ok(response.items.length <= 3)
    assert.equal(fs.existsSync(path.join(cache, 'request-' + id, 'input.txt')), false)
    const log = fs.readFileSync(path.join(cache, 'debug.jsonl'), 'utf8')
    assert.equal(log.includes('heelo'), false)
    assert.equal(log.includes('greeting'), false)
    console.log('Native model ready in', Date.now() - started, 'ms')
  } finally { fs.rmSync(cache, { recursive: true, force: true }) }
})

test('clearing the filter invalidates and cancels a pending request', { timeout: 15000 }, async () => {
  const { cache, filter, state } = setup()
  try {
    const first = filter('accomodate')
    const id = first.variables.spell_request_id
    filter('')
    for (let i = 0; i < 40 && state(id).status === 'loading'; i++) await delay(100)
    assert.equal(state(id).status, 'cancelled')
    assert.equal(fs.existsSync(path.join(cache, 'request-' + id, 'input.txt')), false)
  } finally { fs.rmSync(cache, { recursive: true, force: true }) }
})

test('action diagnostics preserve exact text and do not record it', () => {
  const { cache, env } = setup()
  try {
    const text = 'hello\n$(never execute)\'"'
    const output = execFileSync(binary, ['action', 'paste', text], { env, encoding: 'utf8' })
    assert.equal(output, text)
    const record = JSON.parse(fs.readFileSync(path.join(cache, 'debug.jsonl'), 'utf8').trim())
    assert.equal(record.action, 'paste')
    assert.equal(record.input_length, text.length)
    assert.equal(JSON.stringify(record).includes('never execute'), false)
  } finally { fs.rmSync(cache, { recursive: true, force: true }) }
})

test('dismissal stops polling and cancels model work without a UI callback', { timeout: 20000 }, async () => {
  const { cache, filter, state } = setup()
  try {
    const first = filter('definately')
    const id = first.variables.spell_request_id
    // Do not rerun the filter: this is how Alfred behaves after Escape.
    for (let i = 0; i < 150 && state(id).status === 'loading'; i++) await delay(100)
    assert.equal(state(id).status, 'cancelled')
    const records = fs.readFileSync(path.join(cache, 'debug.jsonl'), 'utf8')
    assert.ok(records.includes('request_cancelled'))
  } finally { fs.rmSync(cache, { recursive: true, force: true }) }
})

test('a changed query gets isolated results and invalidates the previous worker', { timeout: 15000 }, async () => {
  const { cache, filter, state } = setup()
  try {
    const first = filter('heelo')
    const oldID = first.variables.spell_request_id
    const second = filter('accomodate', oldID)
    const newID = second.variables.spell_request_id
    assert.notEqual(oldID, newID)
    assert.equal(fs.readFileSync(path.join(cache, 'active'), 'utf8'), newID)
    filter('')
    for (let i = 0; i < 80 && (state(oldID).status === 'loading' || state(newID).status === 'loading'); i++) await delay(100)
    assert.equal(state(oldID).status, 'cancelled')
    assert.equal(state(newID).status, 'cancelled')
  } finally { fs.rmSync(cache, { recursive: true, force: true }) }
})
