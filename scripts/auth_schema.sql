-- MathArchive 회원제 인증 스키마 (직접 인증 방식 — Supabase Auth 미사용)
--
-- Supabase REST/Auth API 가 egress 한도로 차단된 상태에서 동작 가능하도록
-- psycopg2 직결 + bcrypt + Resend 메일로 자체 인증 구현.
--
-- 실행: scripts/migrate_auth_schema.py

-- 이전 Supabase Auth 기반 스키마 정리 (멱등)
drop policy if exists "profiles_self_select"  on public.profiles;
drop policy if exists "profiles_self_insert"  on public.profiles;
drop policy if exists "profiles_self_update"  on public.profiles;
drop policy if exists "profiles_admin_select" on public.profiles;
drop policy if exists "profiles_admin_update" on public.profiles;
drop function if exists public.get_email_by_username(text);
drop function if exists public.get_username_by_email(text);
drop function if exists public.is_current_user_admin();
drop table if exists public.profiles cascade;

-- ── users ───────────────────────────────────────────────────────────────────
create table if not exists public.users (
    user_id        bigserial primary key,
    username       text unique not null,
    name           text not null,
    email          text unique not null,
    password_hash  text not null,
    approved       boolean not null default false,
    is_admin       boolean not null default false,
    created_at     timestamptz not null default now()
);

create index if not exists idx_users_username on public.users(username);
create index if not exists idx_users_email    on public.users(email);
create index if not exists idx_users_pending  on public.users(approved) where not approved;

-- ── password reset tokens ───────────────────────────────────────────────────
create table if not exists public.password_reset_tokens (
    token        text primary key,
    user_id      bigint not null references public.users(user_id) on delete cascade,
    created_at   timestamptz not null default now(),
    expires_at   timestamptz not null,
    used         boolean not null default false
);

create index if not exists idx_reset_user    on public.password_reset_tokens(user_id);
create index if not exists idx_reset_expires on public.password_reset_tokens(expires_at);
