# Evidence log — §1 User & Job

## Câu hỏi nghiên cứu

Trong các hội thoại `in_class`, học viên có thường xuyên cần làm rõ một đoạn/slide ngay tại thời điểm đang học không, và luồng hỏi đáp hiện tại đang fail ở đâu?

## Nguồn và phạm vi

- Nguồn: `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv`.
- Khoảng thời gian trong data pack: 22/07–29/07/2026.
- Quy mô: 2.522 message, tương ứng 1.261 lượt hỏi–đáp; 369 học viên; 585 hội thoại.
- Chỉ phân tích message có `role = student`; dùng `turn_id` để ghép với câu trả lời `role = tutor`.
- Toàn bộ dữ liệu có `conversation_mode = in_class`.

## Phương pháp mining

Đánh dấu một lượt là nhu cầu **làm rõ nội dung** nếu câu hỏi của học viên khớp ít nhất một cụm (không phân biệt hoa/thường):

```regex
giải thích|là gì|nghĩa (là|của)|tại sao|vì sao|hiểu.*(nào|sao)|phân biệt
```

Đây là proxy có thể đếm và tái chạy, không phải nhãn tay hoàn hảo. Nó có thể bỏ sót các câu diễn đạt khác và có thể nhận nhầm một số câu chứa từ khóa. Trước khi dùng làm golden set cần lấy mẫu và gán nhãn tay.

## Kết quả

| Chỉ số | Kết quả |
|---|---:|
| Tổng lượt hỏi của học viên | 1.261 |
| Lượt khớp nhu cầu làm rõ | 578 (45,8%) |
| Học viên có ít nhất một lượt làm rõ | 239/369 (64,8%) |
| Câu trả lời cho nhóm này không có citation | 156/578 (27,0%) |
| Câu trả lời có đặt câu hỏi kiểm tra hiểu | 1/578 (0,17%) |
| Lượt có rating trong nhóm này | 30/578 (5,2%) |
| Down-rating trong phần có rating | 14/30 (46,7%) |

Rating chỉ xuất hiện ở một mẫu rất nhỏ và tự chọn, vì vậy **không** suy rộng tỷ lệ 46,7% cho toàn bộ học viên. Hai dấu hiệu vận hành đáng tin hơn để mô tả khoảng trống hiện tại là 27,0% câu trả lời không có citation và chỉ 1/578 câu trả lời kiểm tra lại mức hiểu.

## Ví dụ nguyên văn

Các trích dẫn dưới đây là đoạn ngắn, đã ẩn danh; mã hội thoại/lượt cho phép truy ngược trong data pack nội bộ.

1. “giải thích 4 chiến lược” — `C0002 / T0959`, trang 45.
2. “tại sao có lưu ý như trang 25” — `C0004 / T0154`, trang 25.
3. “Giải thích đoạn bôi đen ở Trang 15.” — `C0007 / T0020`, trang 15.
4. “"Context" là gì” — `C0013 / T0990`, trang 31.
5. “Designt Pattern ReAct là gì có lưu ý gì về nó?” — `C0015 / T0811`, trang 2.
6. “Giải thích biều đồ đc bôi đỏ” — `C0023 / T0399`, trang 6.
7. “Giải thích slide 4 cho tôi” — `C0266 / T1084`, trang 4; câu trả lời bị down-rating và citation trỏ sang trang 70.
8. “giải thích chi tiết hơn slide 26” — `C0367 / T0466`, trang 26; câu trả lời không tìm thấy dữ liệu, không có citation và bị down-rating.

## Kết luận dùng cho quyết định sản phẩm

Nhu cầu làm rõ nội dung ngay trong buổi học vừa có độ phủ lớn (64,8% học viên), vừa lặp lại nhiều (578 lượt). Luồng hiện tại tiện vì học viên có thể chọn đoạn và hỏi ngay trong trang, nhưng chưa tạo vòng khép kín “giải thích có căn cứ → kiểm tra đã hiểu”. Đây là job đủ cụ thể để tiếp tục so sánh impact ở §2.

