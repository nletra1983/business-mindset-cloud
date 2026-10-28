CREATE TABLE IF NOT EXISTS person (
    id uuid PRIMARY KEY,
    accepting_new boolean NOT NULL DEFAULT false,
    current_model text NOT NULL DEFAULT 'deepseek-chat',
    last_answered_model text NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE person ADD COLUMN IF NOT EXISTS current_model text NOT NULL DEFAULT 'deepseek-chat';
ALTER TABLE person ADD COLUMN IF NOT EXISTS last_answered_model text NULL;

CREATE TABLE IF NOT EXISTS channel_link (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES person (id),
    channel text NOT NULL,
    telegram_user_id bigint UNIQUE NOT NULL,
    telegram_username text NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS run (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES person (id),
    status text NOT NULL,
    step text NOT NULL,
    skill_version text NOT NULL,
    topic_text text NOT NULL,
    access_mode text NOT NULL,
    model_requested text NOT NULL,
    model_returned text NULL,
    telegram_chat_id bigint NOT NULL,
    pinned_message_id bigint NULL,
    in_window boolean NOT NULL DEFAULT false,
    event_answer text NULL,
    scale_answer text NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT run_status_check CHECK (status IN ('open', 'completed')),
    CONSTRAINT run_step_check CHECK (step IN ('event', 'scale', 'finalizing'))
);

CREATE TABLE IF NOT EXISTS utterance (
    id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES run (id),
    speaker text NOT NULL,
    text text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    telegram_message_id bigint NULL,
    CONSTRAINT utterance_speaker_check CHECK (speaker IN ('human', 'agent'))
);

CREATE TABLE IF NOT EXISTS run_summary (
    run_id uuid PRIMARY KEY REFERENCES run (id),
    what_worked text NOT NULL,
    what_weak text NOT NULL,
    what_missed text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS processed_telegram_update (
    update_id bigint PRIMARY KEY,
    processed_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bot_kv (
    key text PRIMARY KEY,
    value text NOT NULL
);
