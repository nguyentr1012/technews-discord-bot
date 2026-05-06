# technews-discord-bot

## Chạy thử trên máy (local)

### Chuẩn bị

- Cài `uv` (khuyến nghị giống GitHub Actions) và cài dependencies:

```bash
uv sync
```

- Tạo file `.env` từ mẫu:

```bash
cp .env.example .env
```

- Điền các biến môi trường cần thiết trong `.env`:
  - `GEMINI_API_KEY`
  - `DISCORD_TOKEN`
  - `DISCORD_CHANNEL_ID`
  - (tuỳ chọn) `DISCORD_GUILD_ID`
  - (tuỳ chọn, nếu bạn dùng Supabase) `SUPABASE_URL`, `SUPABASE_KEY`

### Chạy “1 lần rồi thoát” (không cần cron)

Chạy crawl → tóm tắt → post Discord rồi tự thoát:

```bash
make digest
```

(tương đương `uv run python src/run_once.py`)

### Chạy bot liên tục (và tự chạy theo giờ)

```bash
make bot
```

Sau khi bot online, bạn có thể chạy thủ công ngay lập tức bằng slash command:

- `/digest`: chạy digest ngay bây giờ
- `/ping`: kiểm tra bot còn hoạt động

## Chạy trên GitHub Actions

Workflow `.github/workflows/digest.yml` đã có:

- `schedule` (cron) để chạy hằng ngày
- `workflow_dispatch` để bấm chạy thủ công trên GitHub UI
