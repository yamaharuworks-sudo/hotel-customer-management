<script setup>

defineProps({
    email: String,
    password: String,
    isLoggedIn: Boolean,
    loginError: String
});

const emit = defineEmits([
    "update-email",
    "update-password",
    "submit"
]);

</script>

<template>

    <form class="login-form" @submit.prevent="emit('submit')">
        <h2>管理者ログイン</h2>

        <div class="form-group">
            <label for="email">メールアドレス</label>
            <input id="email" type="email" autocomplete="username" 
                :value="email"
                @input="emit('update-email', $event.target.value)"
                required
            >
        </div>

        <div class="form-group">
            <label for="password">パスワード</label>
            <input 
                id="password" 
                type="password" 
                autocomplete="current-password"
                :value="password"
                @input="emit('update-password', $event.target.value)"
                required
            >
        </div>

        <p v-if="loginError" class="error-message">{{ loginError }}</p>
        <button type="submit" :disabled="isLoggedIn"> {{ isLoggedIn ? "ログイン中..." : "ログイン" }}</button>
    </form>

</template>

<style scoped>
.login-form {
    max-width: 400px;
    margin: 80px auto;
    padding: 32px;
    border: 1px solid #ddd;
    border-radius: 8px;
}
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 20px;
}

.form-group input {
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
}

button {
    width: 100%;
    padding: 12px;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.error-message {
    color: #dc2626;
    font-size: 14px;
}
</style>