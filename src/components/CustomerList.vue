<script setup>

const props = defineProps({
    filteredCustomers: Array
});
const emit = defineEmits(["delete", "edit", "register-stay", "show-history"]);


</script>


<template>
    <p v-if="filteredCustomers.length === 0">該当する顧客が見つかりません。</p>
    <ul v-else class="customer-list">
        <li class="customer-card"
            v-for="customer in filteredCustomers"
            :key="customer.id">
            <p class="customer-name">{{ customer.name }}</p>
            <div class="customer-info">
                <p>電話番号：{{ customer.phone }}</p>
                <p>前回宿泊日：{{ customer.lastStayedDate }}</p>
                <p>宿泊回数：{{ customer.stayCount }}回</p>
                <p>喫煙区分： 
                    {{  customer.smokingPreference === 'non-smoking' ? "禁煙":
                        customer.smokingPreference === 'smoking' ? "喫煙"
                        : "指定なし" 
                    }}
                </p>
                <p>備考： {{ customer.notes  }}</p>
                
            </div>
            
            <div class="customer-actions">
                <button @click="emit('register-stay', customer.id)">宿泊登録</button>
                <button @click="emit('show-history', customer.id)">宿泊履歴</button>
                <button class="edit-button" @click="emit('edit', customer)">編集</button>
                <button class="delete-button" @click="emit('delete', customer.id)">削除</button>
            </div>
            
        </li>
    </ul>


</template>

<style scoped>


.customer-card {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 12px;
}

.customer-list {
    list-style: none;
    padding: 0;
}

.customer-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
}

.customer-actions button {
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
}

.edit-button {
    background-color: #f3f4f6;
    color: #333;
    border: 1px solid #d1d5db;
}

.delete-button {
    background-color: #dc2626;
    color: white;
    border: none;
}

.customer-name {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 12px;

}

.customer-card p {
    margin: 0;
}

.customer-info p{
    margin: 0 0 6px;
}

</style>