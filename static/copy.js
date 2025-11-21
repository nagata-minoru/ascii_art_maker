(text) => {
  // 簡易トーストを表示してコピー結果を知らせる
  const showToast = (message, type = "success") => {
    const old = document.getElementById("ascii-art-toast");
    if (old) {
      old.remove();
    }

    const toast = document.createElement("div");
    toast.id = "ascii-art-toast";
    toast.textContent = message;

    const variantClass = type === "error" ? "toast-error" : "toast-success";
    toast.classList.add(variantClass);

    document.body.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.add("show");
    });

    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => {
        toast.remove();
      }, 250);
    }, 2000);
  };

  // クリップボードに書き込んで、結果に応じてトーストを表示
  if (navigator && navigator.clipboard && text) {
    navigator.clipboard.writeText(text)
      .then(() => {
        showToast("コピーしました！", "success");
      })
      .catch(() => {
        showToast("コピーに失敗しました。", "error");
      });
  } else {
    showToast("クリップボードへのコピーに対応していません。", "error");
  }
}
