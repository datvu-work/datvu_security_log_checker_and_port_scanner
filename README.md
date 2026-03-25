# SecTool 🛡️

**SecTool** là một công cụ dòng lệnh (CLI) bằng Python được thiết kế để giúp các kỹ sư bảo mật nhanh chóng quét các cổng (port) đang mở và kiểm tra xem các địa chỉ IP trong file log có khớp với danh sách đen (blacklist) mã độc đã biết hay không.

## 🛠️ Tính năng chính

* **Quét Port (Port Scanning):** Quét các cổng TCP của một IP mục tiêu.
* **Kiểm tra IP đơn lẻ:** Kiểm tra nhanh một địa chỉ IP cụ thể có nằm trong blacklist hay không.
* **Phân tích File Log:** Đọc qua các file log (`.txt`, `.csv`, `.json`), trích xuất địa chỉ IP và đối soát với blacklist.
* **Cảnh báo theo ngữ cảnh:** Khi tìm thấy IP độc hại, công cụ sẽ in ra chính xác số dòng và nội dung dòng log đó để bạn dễ dàng điều tra.
* **Tùy chỉnh Blacklist:** Hỗ trợ sử dụng file blacklist riêng của bạn. Nếu không cung cấp, công cụ sẽ dùng file mặc định.
* **Lưu kết quả:** Xuất kết quả quét hoặc kiểm tra ra file text để phục vụ báo cáo.
---

### Tech Stack
Python 3 (Standard Libraries) vì các lý do chiến lược:

* Zero Dependencies: Công cụ không yêu cầu cài đặt thư viện ngoài (pip install), giúp triển khai ngay lập tức trên các server bảo mật bị hạn chế internet.

* Hiệu suất bộ nhớ (Memory Efficiency): Sử dụng Python Generators (yield) để đọc file theo từng dòng (streaming), cho phép xử lý các file log hàng chục GB mà không gây tràn RAM.

* Tốc độ: Sử dụng concurrent.futures (Multithreading) để thực hiện quét cổng song song, giảm thời gian chờ đợi từ vài phút xuống vài giây.

* Tính linh hoạt: Hỗ trợ đa định dạng (TXT, CSV, JSON) giúp công cụ tương thích với nhiều nguồn dữ liệu khác nhau.

## 📂 Cấu trúc dự án

```text
sectool/
├── src/                # Mã nguồn chính của ứng dụng
│   ├── main.py         # Điểm chạy chính (Entry point)
│   ├── scanner.py      # Module quét cổng
│   ├── checker.py      # Module đối soát IP
│   ├── extractors.py   # Module trích xuất IP từ log
│   └── utils.py        # Các hàm tiện ích và cấu hình màu sắc
├── tests/              # Các kịch bản kiểm thử tự động (Unit Tests)
├── data/               # Thư mục chứa các file log mẫu
├── main_blacklist.txt  # Danh sách đen mặc định (Threat Intel)
├── setup.sh            # Script cài đặt môi trường và cấp quyền
└── README.md           # Tài liệu hướng dẫn
le_auth.log` - File log xác thực Linux giả lập để test trích xuất IP.

## 🚀 Cài đặt

Công cụ này chỉ sử dụng các thư viện chuẩn của Python. Bạn không cần cài đặt thêm bất kỳ gói thư viện bên ngoài nào (không cần `pip install`).

```bash
# Clone repository
git clone [https://github.com/yourusername/sectool.git](https://github.com/yourusername/sectool.git)
cd sectool
```
## Cấp quyền thực thi cho script
```bash
chmod +x setup.sh
./setup.sh
```
Lưu ý: Script này sẽ tạo một lệnh tắt sectool để bạn có thể chạy ở bất cứ đâu.

## 📖 Cách sử dụng
Bạn có thể chạy trực tiếp bằng lệnh sectool (nếu đã chạy setup) hoặc python3 src/main.py.

Công cụ có hai lệnh chính: `scan` (để quét cổng) và `check` (để kiểm tra danh sách đen).

### 1. Kiểm tra Log và IP đối chiếu với Blacklist (danh sách IP độc hại)  (`check`)

Theo mặc định, công cụ sẽ tìm tệp danh sách đen có tên `main_blacklist.txt` trong cùng thư mục.

**Kiểm tra một địa chỉ IP đơn lẻ:**
```bash
sectool check 185.156.74.65
```
**Kiểm tra một tệp Log trong folder data (như syslog hoặc auth.log):**
```bash
sectool check data/sample_auth.log
```
**Kiểm tra một tệp nhật ký CSV bằng danh sách đen tùy chỉnh và lưu kết quả đầu ra vào một tệp:**
```bash
./sectool.py check sample_log.csv -t csv -b blacklist.csv -w report.txt
```
### 2. Quét Cổng đang mở (port scanning)

Công cụ quét kiểm tra các cổng TCP đang mở. Nó không yêu cầu quyền root hoặc sudo.

**Quét các cổng mặc định (từ 1 đến 1024):**
```bash
sectool scan 192.168.1.1
```
**Quét một dải cổng cụ thể và lưu kết quả vào một tệp:**
```bash
sectool scan 10.0.0.5 -p 80-8080 -w open_ports.txt
```
### 3. Giải thích các Tham số (Arguments)
<img width="1440" height="599" alt="image" src="https://github.com/user-attachments/assets/a0293ef2-a70e-4ffa-9023-7bd065ac70ff" />
<img width="1443" height="1323" alt="image" src="https://github.com/user-attachments/assets/af5c5e5c-6250-4bc9-903c-0f6157bc0c63" />
<img width="1444" height="944" alt="image" src="https://github.com/user-attachments/assets/223b7760-6b40-4943-9bd6-ad2acb8b2d08" />

**Ví dụ kết hợp nâng cao**
Kịch bản: Bạn muốn kiểm tra một file log của Firewall định dạng JSON, sử dụng một danh sách đen riêng của công ty và muốn lưu kết quả lại để gửi cho sếp.
```bash
sectool check logs/firewall.json -t json -b company_threats.json -w investigation_report.txt
```
Giải thích lệnh trên:

* check logs/firewall.json: Đối tượng kiểm tra là file log JSON.


* -t json: Báo cho công cụ biết đây là cấu trúc JSON để nó phân tích sâu vào các key/value.

* -b company_threats.json: Thay vì dùng file mặc định, hãy dùng dữ liệu độc quyền của công ty.

* -w investigation_report.txt: Mọi kết quả tìm thấy sẽ được ghi vào file investigation_report.txt.

## Video demo dự án
https://drive.google.com/file/d/15G5ySRuLMrBwENUF3-rresjjvNU6sDIp/view?usp=sharing


