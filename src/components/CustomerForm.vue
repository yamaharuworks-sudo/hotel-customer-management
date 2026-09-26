<script setup>  
const props = defineProps({
    newName: String,
    newPhone: String,
    lastStayedDate: String,
    stayCount: Number,
    editingId: {
        type: Number,
        default: null
    },
    nameError: String,
    phoneError: String,
    smokingPreference: String,
    notes: String

})

const emit = defineEmits(
    ["update-name", 
    "update-phone", 
    "update-last-stayed-date", 
    "update-stay-count",
    "update-smoking-preference",
    "update-notes",
    "submit",
    "clear-name-error",
    "clear-phone-error",
    "cancel"])

</script>

<template>

<form class="customer-form" 
    @submit.prevent="emit('submit')">
    <div class="form-group">
        <label>氏名</label>
        <input 
            :value="newName"
            @input="
            emit('update-name', $event.target.value); 
            emit('clear-name-error')
            "
            type="text"
        >
        <p v-if="nameError" class="error-message">{{ nameError }}</p>
    </div>
    <div class="form-group">
        <label>電話番号</label>
        <input 
            :value="newPhone"
            @input="
            emit('update-phone',$event.target.value);
            emit('clear-phone-error')
            "
            type="text"
        >
        <p v-if="phoneError" class="error-message">{{ phoneError }}</p>
    </div>
        
    <div class="form-group">
        <label>前回宿泊日</label>
        <input 
            :value="lastStayedDate"
            @input="emit('update-last-stayed-date', $event.target.value)"
            type="Date"
        >
    </div>

    <div class="form-group">
        <label>宿泊回数</label>
        <input 
            :value="stayCount"
            @input="emit('update-stay-count', Number($event.target.value))"
            type="number"
        >
    </div>

    <div class="form-group">
        <label>喫煙区分</label>
        <input 
            :checked="smokingPreference === 'non-smoking'"
            type="radio" 
            name="smokingPreference"
            value="non-smoking" 
            @change="emit('update-smoking-preference', 'non-smoking')"
        >禁煙
        <input 
            :checked="smokingPreference === 'smoking'"
            type="radio" 
            name="smokingPreference"
            value="smoking"
            @change="emit('update-smoking-preference', 'smoking')"
        >喫煙
        <input
            :checked="smokingPreference === 'none'"
            type="radio" 
            name="smokingPreference"
            value="none"
            @change="emit('update-smoking-preference', 'none')"
        >指定なし
    </div>

    <div class="form-group">
        <label>備考</label>
        <textarea
        :value="notes"
        @input="emit('update-notes', $event.target.value)"
        ></textarea>
    </div>

    <div class="form-actions">
        <button class="cancel-button"
            @click="emit('cancel')"
            v-if="editingId !== null"
            type="button">キャンセル
        </button>
        <button class="submit-button" type="submit">
            {{editingId === null ? "登録" : "更新"}}
        </button>
    </div>
    
</form>

</template>

<style scoped>
.customer-form {
    padding: 24px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-top: 32px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 16px;
}
.form-group input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-sizing: border-box;
}
.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}

.form-actions button {
    padding: 10px 18px;
    border-radius: 6px;
    cursor: pointer;
}

.submit-button {
    background-color: #2563eb;
    color: white;
    border: none;
}
.cancel-button {
    background-color: white;
    color: #555;
    border: 1px solid #ccc;
}
.error-message {
    color: #dc2626;
    font-size: 14px;
    margin: 2px 0 0;
}
</style>