<script setup>

const props = defineProps({
    stayHistory:Array,
    stayDeleteError: String
});

const emit = defineEmits(["delete-stay", "close"]);


</script>


    <template>
    <div>
        <h3>宿泊履歴</h3>
        <p v-if="stayDeleteError">{{ stayDeleteError }}</p>
        
        <div v-if="stayHistory.length > 0 ">
        <div v-for="stay in stayHistory" :key="stay.id">
            <p>宿泊日： {{ stay.stay_date }}</p>
            <p>備考： {{ stay.notes }}</p>
            <button @click="emit('delete-stay', stay.id)">削除</button>
        </div>
        </div>
        <p v-else>宿泊履歴はありません</p>

        <button @click="emit('close')">閉じる</button>

    </div>
    
</template>