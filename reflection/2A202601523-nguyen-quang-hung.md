# Reflection — Nguyễn Quang Hưng

**Mã học viên:** 2A202601523

## Vai trò: Build

Prototype "Nói Lại Đi" (`codebase/noi-lai-di/`) — phần người dùng thật sự chạm vào và là thứ đem đi demo: UI/UX, luồng end-to-end, nối backend, live demo.

## Tôi đã làm

Điểm xuất phát là một quan sát về giao diện, không phải về mô hình. VLearn hiện cho học viên ba lựa chọn khi bôi đen một đoạn slide — `Hỏi AI` · `Báo bối rối` · `Ghi chú` — cộng bảy công cụ đánh dấu. Cả mười thứ đều giữ học viên ở thế **nhận vào**; không có động từ nào bắt học viên **nói ra**. Tôi thêm động từ thứ tư — `Nói lại` — vào đúng menu đó, thay vì mở một màn hình mới.

- **Reader PDF thật**: vẽ từng trang bằng PDF.js, vendor hoá trong repo — chạy offline, không `npm install`, không cần API key.
- **Luồng học có chốt**: tải slide → tách Knowledge Unit → sau mỗi KU chèn slide chốt, chưa qua chốt thì không đọc tiếp được. Mỗi KU gồm **3 câu tự luận + 3 câu trắc nghiệm**, không thay thế nhau.
- **Peek có đếm + Mastery %**: bản đầu tôi khoá cứng slide khi đang làm bài; sau khi xem UI của Tuấn, tôi đổi sang cho phép hé nhìn lại tài liệu nhưng **đếm số lần hé** và trừ vào Mastery — giữ được áp lực retrieval mà không biến sản phẩm thành cai ngục.
- **Bền trạng thái**: slide đã tải lên và kết quả từng phiên còn nguyên sau khi F5 (localStorage + IndexedDB).
- **Nối backend thật**: `ensureSession()` mở learning session, `evaluate()` gọi `POST /learning-sessions/{id}/answers` rồi ánh xạ `correct_points` / `missing_points` về đúng các ý của thẻ; `grade()` rule-based làm fallback.
- **Vá backend khi cần**: thêm CORS vào `app/main.py`; sửa câu tự luận để chỉ trả đáp án tham chiếu **sau** khi nộp bài (trước đó có đường lộ đáp án — vi phạm chính `answer_leak = False` mà spec §7 đã khai).
- **`run-all.py`**: chạy cả backend lẫn giao diện bằng một lệnh, để lúc demo không ai phải nhớ hai cổng.

Hai chi tiết nhỏ nhưng cố ý: chữ do LLM trả về được **escape trước khi nhét vào `innerHTML`** (không tin output của mô hình như tin dữ liệu của mình), và **bỏ dấu khi so khớp** để học viên gõ không dấu vẫn được tính đúng.

## Quyết định quan trọng nhất

**Không để AI "chấm điểm độ hiểu".**

Chấm độ hiểu là việc chủ quan, không có đáp án đúng để đối chiếu, sai thì học viên mất niềm tin ngay — đúng lớp chỗ khó ④. Tôi định nghĩa lại quyết định trung tâm thành một việc kiểm chứng được: **so câu trả lời với danh sách "ý bắt buộc" của đoạn nguồn — ý nào có, ý nào thiếu.** Mỗi ý bắt buộc trace được về một câu có thật trong slide (`data-src`), nên người thứ hai mở đoạn nguồn ra là chấm lại được cùng kết quả.

Hệ quả là phản hồi ba phần — *đã nắm* / *chưa nhắc tới* / *chỗ tài liệu nói ý này* — thay vì một con điểm. Học viên cãi được với hệ thống, và cãi có căn cứ. Phép thử tôi để sẵn trong README chứng minh hệ thống **đo hiểu chứ không đo từ vựng**: câu gọi đúng tên "Q K V, multi-head, softmax" mà không nói chúng làm gì thì bị chỉ ra là thiếu; câu diễn đạt dân dã "mỗi chữ được ngó lại mấy chữ đứng trước nó, rồi tự cân xem chữ nào dính tới mình nhiều nhất" thì được tính đủ ý.

## Điều tôi học được

**Từ case fail của nhóm: FE luôn rơi về chấm cục bộ dù backend đang chạy tốt.**

Triệu chứng là giao diện hiện nhãn "Bản offline ước lượng theo độ đầy đủ" trong khi backend chạy bình thường, 118/118 test pass. Thứ đánh lạc hướng là log backend **toàn 2xx** — `POST /documents/upload` trả `201 Created` sạch sẽ, nhìn log thì kết luận "backend ổn, lỗi ở FE". Nguyên nhân thật: FE ở cổng 8899, backend ở 8000 → hai origin khác nhau; không có CORS thì trình duyệt **vẫn gửi** request (nên server ghi log 201) nhưng **chặn response**, `fetch` ném lỗi ngay tại `.json()`, rơi vào `catch`, quay về chấm cục bộ. Vì thế `/process` không bao giờ được gọi. Cùng họ với nó là một lỗi thứ hai: bấm **Gửi** sớm hơn lúc phiên học mở xong cũng làm câu tự luận rơi về chấm cục bộ.

Bài học: **fallback êm ái là con dao hai lưỡi.** Tôi viết `evaluate()` với tinh thần "demo không bao giờ vỡ" — backend chết thì tự quay về `grade()`. Đứng ở góc trải nghiệm thì đúng (PAIR Graceful Failure). Đứng ở góc đo lường thì cái fallback đó đã che mất một sự thật nghiêm trọng: **suốt một quãng, sản phẩm chạy trơn tru mà không có một lời gọi AI thật nào.** Nếu demo hôm đó, nhóm đã trình bày một hệ thống "AI chấm bài" mà AI không hề tham gia, và không ai trong phòng nhận ra — kể cả nhóm. Thứ cứu chúng tôi không phải test, mà là **cái nhãn** trên màn hình: đó là lý do duy nhất chúng tôi biết mình đang ở chế độ nào. Nguyên tắc tôi giữ từ đây: hệ thống có fallback **phải luôn khai báo nó đang chạy ở nhánh nào** — trên giao diện và trong log. Fallback im lặng không phải graceful failure, nó là hệ thống nói dối cả người dùng lẫn đội build. Điều này khớp thẳng với rubric R5: có lời gọi AI thật ở quyết định trung tâm, và **phần mock phải ghi rõ**.

Một case fail thứ hai cùng bài học, ở phía đo: lượt eval đầu chỉ **75% (15/20)** vì Evaluator trừ `Correctness` quá nặng với câu trả lời chỉ **thiếu ý** chứ không sai; nhóm tách bạch `Correctness` khỏi `Coverage` rồi lên **100% (20/20)**. Với tôi đây cũng là chuyện giao diện: nếu màn hình chỉ hiện một con điểm, học viên trả lời đúng-nhưng-thiếu sẽ đọc thành "mình sai" và mất động lực — chính là lý do tôi giữ phản hồi ba phần thay vì một con số.

**Về cách dùng AI để build.** Tôi dùng AI cho gần như toàn bộ phần code — dựng pipeline render PDF.js, sinh khung state, viết lớp gọi API — rút phần cơ khí từ nhiều giờ xuống vài chục phút. Nhưng phân công thực tế khá rõ: AI làm nhanh phần tôi đã mô tả được đầu vào/đầu ra/điều kiện biên; AI hay **sửa đúng triệu chứng ở sai tầng** (khi tôi nói "FE không gọi được backend" thì hướng sửa đi vào FE — chỉ khi tôi đưa **bằng chứng thô** là log 201 rồi im lặng mới lần ra tầng đúng); còn các đánh đổi sản phẩm — so ý bắt buộc thay vì chấm điểm, peek-có-đếm thay vì khoá cứng, nhét `Nói lại` vào menu sẵn có thay vì mở màn hình mới — thì AI không quyết hộ được. Gọn lại: **mô tả triệu chứng thì nhận về bản vá; đưa bằng chứng thì nhận về chẩn đoán.**

## Nếu làm lại, tôi sẽ

1. **Kiểm tra "AI có thật sự được gọi không" ngay từ lần nối đầu tiên**, bằng một trace đếm số lời gọi hiển thị trên UI — thay vì tin vào việc màn hình chạy mượt.
2. **Nối backend sớm hơn.** Tôi xây FE chạy độc lập trước rồi mới nối, nên toàn bộ lớp lỗi tích hợp (CORS, race điều kiện phiên, lệch schema) dồn hết vào buổi sáng ngày 2.
3. **Đặt nhãn chế độ thành thành phần bắt buộc**, không phải một dòng chữ tôi tình cờ viết cho tử tế.
4. **Ngồi cạnh người test sớm hơn.** Chi tiết "gõ không dấu" và "peek thay vì khoá cứng" đều đến từ việc nhìn người khác dùng, không đến từ việc tôi ngồi nghĩ.
