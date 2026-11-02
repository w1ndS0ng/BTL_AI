# Backbone bài tập lớn AI số 1

Dự án cài đặt Tic-Tac-Toe tổng quát `m x n`, thắng khi có `k` quân liên tiếp. Cấu hình mặc định cho bài lớn là bàn `9x9`, `k=5`; cấu hình `3x3`, `k=3` được dùng để kiểm chứng chính sách MCTS không thua trước đối thủ tối ưu.

## Thành phần

- Minimax có cắt tỉa Alpha-Beta, giới hạn độ sâu và sắp thứ tự nước đi.
- MCTS dùng UCT với `c` cấu hình được.
- Hai kiểu rollout: ngẫu nhiên và heuristic.
- CLI chơi người với máy hoặc cho hai AI đấu nhau.
- Bộ chạy thực nghiệm xuất CSV/JSON và vẽ đồ thị nếu có `matplotlib`.
- Kiểm thử cho luật chơi, Minimax và MCTS.

## Yêu cầu

- Python 3.10 trở lên.
- PowerShell hoặc terminal tương đương.
- `matplotlib` chỉ cần khi muốn tạo đồ thị PNG.

## Cài đặt trên Windows

Mở PowerShell tại thư mục dự án `D:\pro\prj AI`, sau đó chạy lần lượt:

```powershell
# 1. Tạo môi trường Python riêng cho dự án
python -m venv .venv

# 2. Kích hoạt môi trường
.venv\Scripts\Activate.ps1

# 3. Cài dự án và thư viện vẽ đồ thị
python -m pip install --upgrade pip
python -m pip install -e ".[plot]"
```

Nếu PowerShell chặn script kích hoạt, cho phép trong phiên hiện tại rồi thử lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Sau khi cài thành công, ba lệnh `tictactoe-play`, `tictactoe-experiment` và `tictactoe-validate` sẽ dùng được trong môi trường `.venv`.

## Chơi Tic-Tac-Toe

### Người đấu với MCTS

```powershell
tictactoe-play --x human --o mcts --size 9 --win-length 5 --iterations 1000
```

Trong đó người chơi cầm `X` và đi trước. Khi chương trình hỏi nước đi, nhập `hàng cột`, ví dụ:

```text
X, enter row and column: 4 4
```

Chỉ số hàng và cột bắt đầu từ `0`. Với bàn `9x9`, chỉ số hợp lệ là từ `0` đến `8`.

### Cho hai AI đấu nhau

```powershell
# Minimax đi trước, MCTS đi sau trên bàn 3x3
tictactoe-play --x minimax --o mcts --size 3 --win-length 3 --iterations 1500

# MCTS dùng rollout heuristic đấu với đối thủ ngẫu nhiên
tictactoe-play --x mcts --o random --size 9 --win-length 5 --iterations 1000 --rollout heuristic
```

Các loại người chơi hợp lệ cho `--x` và `--o`:

- `human`: người nhập nước đi.
- `random`: chọn nước ngẫu nhiên.
- `minimax`: Minimax có Alpha-Beta.
- `mcts`: MCTS dùng UCT.

Các tham số chơi quan trọng:

- `--size`: kích thước bàn vuông, mặc định `9`.
- `--win-length`: số quân liên tiếp để thắng, mặc định `5`.
- `--depth`: độ sâu Minimax; nếu bỏ qua, bàn 3x3 được giải hết và bàn lớn dùng độ sâu `3`.
- `--iterations`: số vòng lặp MCTS, mặc định `1000`.
- `--c`: hằng số khám phá UCT, mặc định `1.4`.
- `--rollout`: `random` hoặc `heuristic`.
- `--seed`: seed ngẫu nhiên để có thể lặp lại kết quả.

Xem toàn bộ tùy chọn bằng:

```powershell
tictactoe-play --help
```

## Chạy kiểm thử

Từ thư mục gốc của dự án, chạy:

```powershell
python -m unittest discover -s tests -v
```

Kết quả hợp lệ phải kết thúc bằng `OK`.

## Kiểm chứng MCTS không thua trên bàn 3x3

Lệnh sau cho MCTS đấu với Minimax tối ưu, đồng thời đổi bên đi trước giữa các ván:

```powershell
tictactoe-validate --games 50 --iterations 3000 --c 1.4 --seed 42
```

Nếu không ghi nhận ván thua, chương trình in:

```text
PASS: no loss observed against optimal Minimax.
```

Đây là kiểm chứng thực nghiệm trên số ván đã chạy, không phải chứng minh hình thức rằng MCTS luôn không thua với mọi seed và mọi ngân sách iteration.

## Chạy thực nghiệm

### Chạy nhanh để kiểm tra chương trình

```powershell
tictactoe-experiment --quick
```

Chế độ này dùng ít ván và ít iteration, phù hợp để xác nhận pipeline xuất dữ liệu hoạt động.

### Chạy theo cấu hình của đề bài

```powershell
tictactoe-experiment `
  --games 50 `
  --iterations 100 500 1000 2000 5000 `
  --c-values 0.5 1.0 1.4 2.0 `
  --rollouts random heuristic `
  --seed 42 `
  --output results
```

Quá trình đầy đủ có thể mất thời gian vì mỗi tổ hợp `c`, iteration và rollout đều chạy nhiều ván. Có thể giảm `--games` hoặc số giá trị trong `--iterations` khi phát triển.

Xem các tham số thực nghiệm bằng:

```powershell
tictactoe-experiment --help
```

## Chạy không cần cài package

Nếu chưa muốn chạy `pip install -e`, có thể đặt thư mục `src` vào `PYTHONPATH` trong phiên PowerShell hiện tại:

```powershell
$env:PYTHONPATH = "src"

python -m tictactoe_ai.cli --x human --o mcts --size 9 --win-length 5
python -m tictactoe_ai.validate --games 10 --iterations 1000
python -m tictactoe_ai.experiments --quick
```

## Ví dụ chạy nhanh tổng hợp

```powershell
# Chạy test
python -m unittest discover -s tests -v

# Hai AI đấu nhau
tictactoe-play --x minimax --o mcts --size 3 --win-length 3 --iterations 1500

# Sinh dữ liệu thử nghiệm nhanh
tictactoe-experiment --quick

# Kiểm chứng MCTS
tictactoe-validate --games 50 --iterations 3000
```

## Dữ liệu phục vụ báo cáo

`tictactoe-experiment` tạo:

- `results/mcts_sweep.csv`: thắng/hòa/thua và thời gian theo `c`, iterations, rollout.
- `results/minimax_nodes.csv`: số nút Minimax có và không có Alpha-Beta.
- `results/root_stats.csv`: `W`, `N`, `W/N` tại các con của nút gốc.
- `results/summary.json`: cấu hình và kết quả tổng hợp.
- `results/win_rate.png`: đồ thị iterations - tỷ lệ thắng nếu cài `matplotlib`.

Mở `mcts_sweep.csv` bằng Excel để lập bảng kết quả. File `win_rate.png` có thể đưa trực tiếp vào phần kết quả của báo cáo sau khi kiểm tra nhãn và cấu hình thực nghiệm.

## Đề xuất phát triển tiếp

- Bổ sung giao diện đồ họa bằng Pygame/Tkinter.
- Chạy nhiều seed hơn và thêm khoảng tin cậy.
- Tối ưu bàn lớn bằng Zobrist hashing, transposition table và progressive widening.
- Mở rộng mô hình trạng thái/nước đi cho cờ tướng.

