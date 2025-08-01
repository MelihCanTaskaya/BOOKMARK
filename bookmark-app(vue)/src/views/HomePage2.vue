<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-3xl mx-auto">
      <h1 class="text-3xl font-bold mb-6 text-center">Yer İmlerim</h1>

      <!-- Form -->
      <form @submit.prevent="addBookmark" class="bg-white rounded-2xl shadow p-6 mb-8">
        <div class="flex flex-col gap-4">
          <input
            v-model="newBookmark.url"
            placeholder="URL"
            required
            class="input"
          />
          <input
            v-model="newBookmark.title"
            placeholder="Başlık"
            required
            class="input"
          />
          <div class="flex gap-2">
            <input
              v-model="newTag"
              @keyup.enter="addTag"
              placeholder="Etiket ekle"
              class="input flex-1"
            />
            <button type="submit" class="btn-primary">Ekle</button>
          </div>

          <div class="flex flex-wrap gap-2">
            <span
              v-for="(tag, idx) in newBookmark.tags"
              :key="idx"
              class="tag"
              @click="removeTag(idx)"
            >
              {{ tag }} ×
            </span>
          </div>
        </div>
      </form>

      <!-- Bookmark Cards -->
      <div class="space-y-6">
        <div
          v-for="tag in tagOrder"
          :key="tag"
          class="bg-white p-4 rounded-2xl shadow"
        >
          <h2 class="text-lg font-semibold mb-2 text-blue-600">#{{ tag }}</h2>
          <div class="space-y-2">
            <div
              v-for="bm in filteredBookmarks(tag)"
              :key="bm.id"
              class="p-4 bg-gray-100 rounded-xl flex justify-between items-center"
            >
              <a :href="bm.url" target="_blank" class="text-blue-700 hover:underline">{{ bm.title }}</a>
              <button @click="deleteBookmark(bm.id)" class="text-sm text-red-500 hover:underline">Sil</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { getToken } from '../utils/auth';

export default {
  data() {
    return {
      bookmarks: [],
      newBookmark: { url: '', title: '', tags: [] },
      newTag: '',
      tagOrder: []
    };
  },
  mounted() {
    this.fetchBookmarks();
  },
  methods: {
    async fetchBookmarks() {
      try {
        const res = await fetch("http://localhost:5000/api/bookmarks/", {
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        const data = await res.json();
        this.bookmarks = Array.isArray(data) ? data : [];

        const tagSet = new Set();
        this.bookmarks.forEach(bm => {
          if (bm.tags?.length) bm.tags.forEach(t => tagSet.add(t));
          else tagSet.add("(Tagsiz)");
        });
        this.tagOrder = Array.from(tagSet);
      } catch (err) {
        console.error("Listeleme hatası:", err);
      }
    },
    async addBookmark() {
      try {
        const res = await fetch("http://localhost:5000/api/bookmarks/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getToken()}`,
          },
          body: JSON.stringify(this.newBookmark),
        });
        if (res.ok) {
          await this.fetchBookmarks();
          this.newBookmark = { url: '', title: '', tags: [] };
          this.newTag = '';
        }
      } catch (err) {
        console.error("Ekleme hatası:", err);
      }
    },
    async deleteBookmark(id) {
      try {
        const res = await fetch(`http://localhost:5000/api/bookmarks/${id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${getToken()}` },
        });
        if (res.ok) {
          this.bookmarks = this.bookmarks.filter((b) => b.id !== id);
        }
      } catch (err) {
        console.error("Silme hatası:", err);
      }
    },
    addTag() {
      const tag = this.newTag.trim();
      if (tag && !this.newBookmark.tags.includes(tag)) {
        this.newBookmark.tags.push(tag);
        this.newTag = "";
      }
    },
    removeTag(idx) {
      this.newBookmark.tags.splice(idx, 1);
    },
    filteredBookmarks(tag) {
      if (tag === "(Tagsiz)") return this.bookmarks.filter(bm => !bm.tags?.length);
      return this.bookmarks.filter(bm => bm.tags?.includes(tag));
    },
  }
}
</script>

<style scoped>
.input {
  @apply border rounded-xl px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400;
}
.btn-primary {
  @apply bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700;
}
.tag {
  @apply px-3 py-1 bg-blue-100 text-blue-700 rounded-full cursor-pointer hover:bg-blue-200;
}
</style>
