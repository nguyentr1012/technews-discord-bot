# technews-discord-bot




Sau khi bot online, bạn có thể chạy thủ công ngay lập tức bằng slash command:

- `/digest`: chạy digest ngay bây giờ
- `/ping`: kiểm tra bot còn hoạt động

## Chạy trên GitHub Actions

Workflow `.github/workflows/digest.yml` đã có:

- `schedule` (cron) để chạy hằng ngày
- `workflow_dispatch` để bấm chạy thủ công trên GitHub UI
