<script setup>

import {ref} from "vue";


const stayDate = ref("");
const stayNotes = ref("");
const stayDateError = ref("");

const props = defineProps({
    staySubmitError: String,
    isStaySubmitting: Boolean
});


const emit = defineEmits(["cancel", "add-stay"]);

function handleStaySubmit() {
    if (stayDate.value === "") {
        stayDateError.value = "宿泊日を入力してください";
        return;
    } 
    stayDateError.value = "";
    emit("add-stay", {
        stayDate: stayDate.value, 
        notes: stayNotes.value
        }
    );
}
    

</script>

<template>

    <form @submit.prevent="handleStaySubmit" >
        <input v-model="stayDate" @input="stayDateError=''" type="date" >
        <p v-if="stayDateError">{{ stayDateError }}</p> 

        <textarea v-model="stayNotes"></textarea>
        <button type="button" @click="emit('cancel')">キャンセル</button>
        <button :disabled="isStaySubmitting" type="submit">
            {{ isStaySubmitting ? "保存中" : "登録" }}
            </button>
        <p v-if="staySubmitError">{{ staySubmitError }}</p>

    </form> 



</template>