const token = localStorage.getItem("token");
  if (!token) {
    alert("You must log in first.");
    window.location.href = "login.html";
  }

  function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
  }

  const apiBase = "http://localhost:5000/api/bookmarks";
  let isShowingMostVisited = false;

  document.getElementById("bookmark-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const url = document.getElementById("url").value.trim();
    const title = document.getElementById("title").value.trim();
    const tags = document.getElementById("tags").value.split(",").map(t => t.trim()).filter(Boolean);

    const res = await fetch(apiBase + "/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token")
      },
      body: JSON.stringify({ url, title, tags })
    });

    if (res.ok) {
      loadBookmarks();
      document.getElementById("bookmark-form").reset();
    } else {
      alert("Failed to add bookmark.");
    }
  });
  

  async function loadBookmarks() {
    try {

      console.log("Using token:", token); 
      const res = await fetch("http://localhost:5000/api/bookmarks/", {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      const bookmarks = await res.json();
      renderBookmarks(bookmarks);
    } catch (err) {
      console.error("Failed to load bookmarks:", err);
      alert("Failed to load bookmarks: " + err.message);
    }
  }

  function renderBookmarks(bookmarks) {
    const container = document.getElementById("bookmarks");
    container.innerHTML = "";

    for (const b of bookmarks) {
      const el = document.createElement("div");
      el.innerHTML = `
        <div style="border:1px solid #ccc; margin:10px; padding:10px;">
          <strong><a href="${b.url}" target="_blank">${b.title}</a></strong>
          <button onclick="deleteBookmark(${b.id})">Delete</button>
          <button onclick="editBookmark(${b.id}, '${escapeQuotes(b.title)}', '${escapeQuotes(b.url)}')">Edit</button>
          <div>Tags: ${(b.tags || []).join(", ")}</div>
          ${b.visits !== undefined ? `<div>Visits: ${b.visits}</div>` : ""}
          <input type="text" placeholder="New tag" id="tag-${b.id}"/>
          <button onclick="addTag(${b.id})">Add Tag</button>
        </div>
      `;
      container.appendChild(el);
    }
  }

  function escapeQuotes(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
  }

  async function deleteBookmark(id) {
    const res = await fetch(apiBase + "/" + id, {
      method: "DELETE",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token")
      }
    });
    if (res.ok) {
      loadBookmarks();
    } else {
      alert("Delete failed");
    }
  }

  async function editBookmark(id, currentTitle, currentUrl) {
    const newTitle = prompt("New title:", currentTitle);
    const newUrl = prompt("New URL:", currentUrl);

    if (!newTitle || !newUrl) return;

    const res = await fetch(apiBase + "/" + id, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token")
      },
      body: JSON.stringify({ title: newTitle, url: newUrl })
    });

    if (res.ok) {
      loadBookmarks();
    } else {
      alert("Update failed");
    }
  }

  async function addTag(bookmarkId) {
    const tagInput = document.getElementById("tag-" + bookmarkId);
    const tag = tagInput.value.trim();
    if (!tag) return;

    const res = await fetch(`${apiBase}/${bookmarkId}/tags`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token")
      },
      body: JSON.stringify({ tag })
    });

    if (res.ok) {
      tagInput.value = ""; 
      loadBookmarks();
    } else {
      alert("Tag eklenemedi");
    }
  }

  document.getElementById("filter-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const tag = document.getElementById("filter-tag").value.trim();
    if (!tag) {
      loadBookmarks();
      return;
    }

    const res = await fetch(`${apiBase}/filter?tag=${encodeURIComponent(tag)}`, {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token")
      }
    });

    if (res.ok) {
      const bookmarks = await res.json();
      renderBookmarks(bookmarks);
    } else {
      alert("Failed to filter");
    }
  });

  document.getElementById("toggle-most-visited").addEventListener("click", async function () {
    if (isShowingMostVisited) {
      loadBookmarks();
      this.textContent = "Show Most Visited";
      isShowingMostVisited = false;
    } else {
      const res = await fetch(`${apiBase}/stats/most_visited`, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      });

      if (res.ok) {
        const bookmarks = await res.json();
        renderBookmarks(bookmarks);
        this.textContent = "Show All Bookmarks";
        isShowingMostVisited = true;
      } else {
        alert("Failed to load most visited");
      }
    }
  });

  loadBookmarks();