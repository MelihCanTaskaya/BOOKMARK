<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter();

async function login() {
  try {
    const response = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    });
    const result = await response.json();
    
    if (response.ok) {
      // Token'ı localStorage'a kaydet
      localStorage.setItem('token', result.token);
      alert('Login successful!');
      router.push('/bookmarks');
    } else {
      alert(result.error || 'Login failed');
    }
  } catch (error) {
    alert('An error occurred');
    console.error(error);
  }
}


</script>
