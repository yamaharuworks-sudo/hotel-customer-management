<script setup>

import {ref} from "vue";


const stayDate = ref("");
const stayNotes = ref("");


const props = defineProps({
    staySubmitError: String,
    isStaySubmitting: Boolean
})


const emit = defineEmits(["cancel", "add-stay"]);

function handleStaySubmit() {
    emit("add-stay", {
        stayDate: stayDate.value, 
        notes: stayNotes.value
        }
    );
}

</script>

<template>

    <form @submit.prevent="handleStaySubmit" >
        <input v-model="stayDate" type="date" >
        <textarea v-model="stayNotes"></textarea>
        <button type="button" @click="emit('cancel')">キャンセル</button>
        <button :disabled="isStaySubmitting" type="submit">
            {{ isStaySubmitting ? "保存中" : "登録" }}
            </button>
        <p v-if="staySubmitError">{{ staySubmitError }}</p>

    </form> 

</template>