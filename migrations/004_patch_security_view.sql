CREATE OR REPLACE VIEW active_users AS
SELECT username, email FROM users WHERE id > 0;
