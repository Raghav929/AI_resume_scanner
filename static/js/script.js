(function () {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const fileList = document.getElementById("fileList");

  if (!dropzone || !fileInput || !fileList) return;

  function renderFileList(files) {
    if (!files || files.length === 0) {
      fileList.textContent = "";
      return;
    }
    const names = Array.from(files).map((f) => f.name);
    fileList.textContent = `${names.length} file${names.length > 1 ? "s" : ""} selected: ${names.join(", ")}`;
  }

  fileInput.addEventListener("change", () => renderFileList(fileInput.files));

  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dropzone-active");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dropzone-active");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length) {
      fileInput.files = dt.files;
      renderFileList(dt.files);
    }
  });
})();
