-- Seed AlphaForge with a small fleet of demo entities so the frontend has
-- something to display immediately after `alembic upgrade head`.

BEGIN;

INSERT INTO users (id, email, password_hash, full_name, role, is_active, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'admin@alphaforge.local',     '$argon2id$placeholder$admin',     'AlphaForge Admin',  'admin',      true, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000002', 'quant@alphaforge.local',     '$argon2id$placeholder$quant',     'Demo Researcher',   'researcher', true, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000003', 'viewer@alphaforge.local',    '$argon2id$placeholder$viewer',    'Demo Viewer',       'viewer',     true, NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000004', 'service@alphaforge.local',   '$argon2id$placeholder$service',   'Service Account',   'service',    true, NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

INSERT INTO strategies (id, owner_id, name, description, is_public, tags, created_at, updated_at)
VALUES
  ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000002', 'Demo EMA cross', 'Seeded EMA crossover strategy', true,  ARRAY['trend','ema'],     NOW(), NOW()),
  ('11111111-1111-1111-1111-111111111112', '00000000-0000-0000-0000-000000000002', 'Donchian breakout','Trend-following Donchian breakout', false, ARRAY['breakout','trend'], NOW(), NOW()),
  ('11111111-1111-1111-1111-111111111113', '00000000-0000-0000-0000-000000000002', 'Bollinger MR',  'Mean-reversion via Bollinger',  false, ARRAY['mean-revert'], NOW(), NOW())
ON CONFLICT DO NOTHING;

INSERT INTO strategy_versions (id, strategy_id, version, raw_source, parameters, notes, created_at)
VALUES
  ('22222222-2222-2222-2222-222222222221', '11111111-1111-1111-1111-111111111111', 1,
   $$strategy: "EMA cross"
universe: { symbols: [ETH/USDT], timeframe: 1h }
indicators:
  - {name: ema, alias: fast, period: 12}
  - {name: ema, alias: slow, period: 26}
rules:
  - when: cross_up(fast, slow)
    then: buy
    size: 0.2$$,
   '{"fast_period":12,"slow_period":26}'::jsonb, 'initial', NOW())
ON CONFLICT DO NOTHING;

INSERT INTO backtests (id, strategy_id, strategy_version, owner_id, timeframe, start_at, end_at, initial_balance, final_balance, pnl_abs, pnl_pct, sharpe, sortino, max_drawdown, win_rate, trades_count, status, created_at, updated_at)
VALUES
  ('33333333-3333-3333-3333-333333333331', '11111111-1111-1111-1111-111111111111', 1, '00000000-0000-0000-0000-000000000002',
   '1h', NOW() - INTERVAL '30 days', NOW(), 10000, 10880, 880, 8.8, 1.45, 1.92, 0.07, 57.3, 42, 'completed', NOW(), NOW())
ON CONFLICT DO NOTHING;

INSERT INTO signals (id, strategy_id, strategy_version, symbol, action, strength, emitted_at, reasons)
SELECT
  gen_random_uuid(),
  '11111111-1111-1111-1111-111111111111', 1,
  'ETH/USDT',
  CASE WHEN g % 2 = 0 THEN 'buy' ELSE 'close' END,
  0.6 + 0.05 * (g % 3),
  NOW() - (g || ' hours')::INTERVAL,
  CASE WHEN g % 2 = 0 THEN ARRAY['cross_up','rsi_low'] ELSE ARRAY['cross_down'] END
FROM generate_series(0, 11) AS g
ON CONFLICT DO NOTHING;

INSERT INTO audit_jobs (id, requested_by, chain, address, deep, status, risk_score, risk_level, summary, findings, created_at, completed_at)
VALUES
  ('44444444-4444-4444-4444-444444444441', '00000000-0000-0000-0000-000000000002',
   'eth', '0xababababababababababababababababababab', true, 'completed', 72, 'high',
   'Detected blacklist + delegatecall + onlyOwner',
   '[{"category":"bytecode","code":"DELEGATECALL","severity":"high","description":"DELEGATECALL opcode used"},{"category":"source","code":"SOL_BLACKLIST","severity":"high","description":"Blacklist add function present"}]'::jsonb,
   NOW() - INTERVAL '1 hour', NOW())
ON CONFLICT DO NOTHING;

INSERT INTO alerts (id, owner_id, name, rule_type, channels, config, enabled, fire_count, last_fired_at, created_at, updated_at)
VALUES
  ('55555555-5555-5555-5555-555555555551', '00000000-0000-0000-0000-000000000002',
   'ETH/USDT critical anomaly', 'anomaly', ARRAY['telegram','discord'],
   '{"symbol":"ETH/USDT","threshold":0.9}'::jsonb, true, 3, NOW() - INTERVAL '12 minutes', NOW(), NOW())
ON CONFLICT DO NOTHING;

COMMIT;
