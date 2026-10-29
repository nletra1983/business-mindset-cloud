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

CREATE TABLE IF NOT EXISTS visible_profile (
    person_id uuid PRIMARY KEY REFERENCES person (id),
    strengths_text text NOT NULL DEFAULT '',
    weaknesses_text text NOT NULL DEFAULT '',
    self_facts jsonb NOT NULL DEFAULT '[]'::jsonb,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS profile_edit_session (
    person_id uuid PRIMARY KEY REFERENCES person (id),
    step text NOT NULL DEFAULT 'idle',
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT profile_edit_session_step_check CHECK (
        step IN ('idle', 'awaiting_strengths', 'awaiting_weaknesses', 'awaiting_extra_fact')
    )
);

CREATE TABLE IF NOT EXISTS hidden_profile (
    person_id uuid PRIMARY KEY REFERENCES person (id),
    spotting_status text NOT NULL DEFAULT 'не наблюдалось',
    creativity_status text NOT NULL DEFAULT 'не наблюдалось',
    valuing_status text NOT NULL DEFAULT 'не наблюдалось',
    uncertainty_status text NOT NULL DEFAULT 'не наблюдалось',
    resources_status text NOT NULL DEFAULT 'не наблюдалось',
    learning_status text NOT NULL DEFAULT 'не наблюдалось',
    current_focus text NOT NULL DEFAULT 'spotting',
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT hidden_profile_spotting_status_check CHECK (
        spotting_status IN ('не наблюдалось', 'проявляется', 'слабо', 'устойчиво', 'неравномерно')
    ),
    CONSTRAINT hidden_profile_creativity_status_check CHECK (
        creativity_status IN ('не наблюдалось', 'проявляется', 'слабо', 'устойчиво', 'неравномерно')
    ),
    CONSTRAINT hidden_profile_valuing_status_check CHECK (
        valuing_status IN ('не наблюдалось', 'проявляется', 'слабо', 'устойчиво', 'неравномерно')
    ),
    CONSTRAINT hidden_profile_uncertainty_status_check CHECK (
        uncertainty_status IN ('не наблюдалось', 'проявляется', 'слабо', 'устойчиво', 'неравномерно')
    ),
    CONSTRAINT hidden_profile_resources_status_check CHECK (
        resources_status IN ('не наблюдалось', 'проявляется', 'слабо', 'устойчиво', 'неравномерно')
    ),
    CONSTRAINT hidden_profile_learning_status_check CHECK (
        learning_status IN ('не наблюдалось', 'проявляется', 'слабо', 'устойчиво', 'неравномерно')
    ),
    CONSTRAINT hidden_profile_current_focus_check CHECK (
        current_focus IN ('spotting', 'creativity', 'valuing', 'uncertainty', 'resources', 'learning')
    )
);

CREATE TABLE IF NOT EXISTS hidden_profile_evidence (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES person (id),
    run_id uuid NOT NULL REFERENCES run (id),
    exercise_id text NOT NULL,
    characteristic_id text NOT NULL,
    signal text NOT NULL,
    quote_or_paraphrase text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT hidden_profile_evidence_characteristic_check CHECK (
        characteristic_id IN ('spotting', 'creativity', 'valuing', 'uncertainty', 'resources', 'learning')
    ),
    CONSTRAINT hidden_profile_evidence_signal_check CHECK (
        signal IN ('проявляется', 'слабо')
    ),
    CONSTRAINT hidden_profile_evidence_unique_run_characteristic UNIQUE (run_id, characteristic_id)
);

CREATE TABLE IF NOT EXISTS email_link (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES person (id),
    email text NOT NULL UNIQUE,
    confirmed boolean NOT NULL DEFAULT false,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS link_code (
    id uuid PRIMARY KEY,
    kind text NOT NULL,
    destination text NOT NULL,
    code text NOT NULL,
    purpose text NOT NULL,
    requester_person_id uuid NULL REFERENCES person (id),
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT link_code_kind_check CHECK (kind IN ('email', 'telegram')),
    CONSTRAINT link_code_purpose_check CHECK (purpose IN ('login', 'settings')),
    CONSTRAINT link_code_destination_unique UNIQUE (kind, destination)
);

CREATE TABLE IF NOT EXISTS staged_link (
    person_id uuid NOT NULL REFERENCES person (id),
    kind text NOT NULL,
    destination text NOT NULL,
    confirmed boolean NOT NULL DEFAULT false,
    PRIMARY KEY (person_id, kind),
    CONSTRAINT staged_link_kind_check CHECK (kind IN ('email', 'telegram'))
);

CREATE TABLE IF NOT EXISTS kept_profile_text (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES person (id),
    source_label text NOT NULL,
    strengths_text text NOT NULL DEFAULT '',
    weaknesses_text text NOT NULL DEFAULT '',
    self_facts jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
