import React, { useEffect, useState } from "react";

type ApiHealth = "checking" | "ready" | "unavailable";

export default function App() {
  const [apiHealth, setApiHealth] = useState<ApiHealth>("checking");

  useEffect(() => {
    const controller = new AbortController();

    async function checkApi() {
      try {
        const response = await fetch("/health/ready", {
          signal: controller.signal,
          headers: { Accept: "application/json" },
        });

        if (!response.ok) {
          throw new Error("API is not ready");
        }

        setApiHealth("ready");
      } catch {
        if (!controller.signal.aborted) {
          setApiHealth("unavailable");
        }
      }
    }

    void checkApi();

    return () => controller.abort();
  }, []);

  const statusLabel: Record<ApiHealth, string> = {
    checking: "Đang kiểm tra kết nối",
    ready: "Backend và Database đã sẵn sàng",
    unavailable: "Backend hoặc Database chưa sẵn sàng",
  };

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="ST-NLP trang chủ">
          <span className="brand-mark">ST</span>
          <span>
            <strong>ST-NLP</strong>
            <small>SMART TRAFFIC & URBAN INCIDENTS</small>
          </span>
        </a>
        <span className="environment-chip">LOCAL FOUNDATION</span>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">NỀN TẢNG TIẾP NHẬN VÀ PHÂN LOẠI PHẢN ÁNH</p>
          <h1>Giao thông đô thị tốt hơn bắt đầu từ một phản ánh được lắng nghe.</h1>
          <p className="hero-description">
            ST-NLP hướng tới hỗ trợ tiếp nhận phản ánh bằng văn bản, sử dụng
            xử lý ngôn ngữ tự nhiên để đề xuất nhóm vấn đề và hỗ trợ cán bộ
            kiểm duyệt.
          </p>
          <div className={"health-panel health-" + apiHealth} role="status" aria-live="polite">
            <span className="health-dot" />
            <span>{statusLabel[apiHealth]}</span>
          </div>
        </div>

        <aside className="project-card">
          <div className="card-kicker">PROJECT FOUNDATION</div>
          <div className="card-number">11</div>
          <p>Danh mục phản ánh được thống nhất</p>
          <div className="card-divider" />
          <div className="card-number">12</div>
          <p>Bảng dữ liệu trong Database baseline</p>
          <div className="card-note">
            AI đưa ra nhãn đề xuất. Cán bộ có thẩm quyền xác nhận kết quả cuối cùng.
          </div>
        </aside>
      </section>

      <section className="section-heading">
        <div>
          <p className="eyebrow">LỘ TRÌNH HỆ THỐNG</p>
          <h2>Các phân hệ đang được xây dựng</h2>
        </div>
        <span className="foundation-tag">Giai đoạn nền tảng</span>
      </section>

      <section className="module-grid" aria-label="Các phân hệ dự án">
        <article className="module-card">
          <span className="module-index">01</span>
          <h3>Cổng người dân</h3>
          <p>Đăng nhập, gửi phản ánh, ảnh minh chứng, vị trí và theo dõi xử lý.</p>
          <span className="module-state">Chưa triển khai</span>
        </article>
        <article className="module-card">
          <span className="module-index">02</span>
          <h3>Cổng quản trị</h3>
          <p>Tiếp nhận, tra cứu, kiểm duyệt nhãn AI và quản lý trạng thái.</p>
          <span className="module-state">Chưa triển khai</span>
        </article>
        <article className="module-card">
          <span className="module-index">03</span>
          <h3>NLP / Machine Learning</h3>
          <p>Tiền xử lý tiếng Việt, huấn luyện, dự đoán và đánh giá mô hình.</p>
          <span className="module-state">Chưa triển khai</span>
        </article>
        <article className="module-card">
          <span className="module-index">04</span>
          <h3>Dashboard & dữ liệu</h3>
          <p>Thống kê phản ánh, bản đồ và quản lý các phiên bản Dataset/Model.</p>
          <span className="module-state">Chưa triển khai</span>
        </article>
      </section>

      <footer className="footer">
        ST-NLP · Local development foundation · Chưa phải phiên bản nghiệm thu
      </footer>
    </main>
  );
}
