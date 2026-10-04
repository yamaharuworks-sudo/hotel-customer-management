<script setup>
import {ref, computed} from "vue";
import CustomerList from './components/CustomerList.vue'
import CustomerForm from "./components/CustomerForm.vue";
import { useCustomers } from "./composables/useCustomers.js";
import StayHistory from "./components/StayHistory.vue";

const newName = ref("");
const newPhone = ref("");
const nameError = ref("");
const phoneError = ref("");
const editingId = ref(null);
const searchQuery = ref("");
const smokingPreference = ref("none");
const notes = ref("");

// エラーハンドリング用
const submitError = ref("");
const stayDeleteError = ref("");
const customerDeleteError = ref("");
const stayFetchError = ref("");
const staySubmitError = ref("");

// 宿泊登録用
const stayCustomerId = ref(null);


const sortBy = ref("date");

// 宿泊履歴
const stayHistory = ref([]);
const historyCustomerId = ref(null);

// API通信開始　true 終了　false
const isSubmitting = ref(false); //　顧客登録中
const isStaySubmitting = ref(false); 

const {customers, 
        addCustomer, 
        deleteCustomer, 
        updateCustomer, 
        fetchStays,
        deleteStay,
        addStay
      } = useCustomers();


function startEdit(customer) {
  editingId.value = customer.id;
  newName.value = customer.name;
  newPhone.value = customer.phone;
  smokingPreference.value = customer.smokingPreference;
  notes.value = customer.notes;
}


function validateCustomer() {
  let hasError = false;
  const digitsOnly = newPhone.value.replaceAll("-","");

  if (newName.value.trim() === "") {
    nameError.value = "氏名を入力してください";
    hasError = true;
  } else if (newName.value.trim().length > 50) {
    nameError.value = "氏名は50文字以内で入力してください";
    hasError = true;
  }
  if (newPhone.value.trim() === "") {
    phoneError.value = "電話番号を入力してください";
    hasError = true;
  } else if (!/^[0-9-]+$/.test(newPhone.value)) {
    phoneError.value = "番号とハイフンのみ入力してください";
    hasError = true;
  } else if (digitsOnly.length !== 11 && digitsOnly.length !== 10 ) {
    phoneError.value = "10または11桁の数字を入力してください";
    hasError = true;
  }

  return hasError;
}

async function handleSubmit() {
  nameError.value = "";
  phoneError.value = "";
  submitError.value = "";

  const hasError = validateCustomer();

  if (hasError) return;

  const customerData = {
      name: newName.value,
      phone: newPhone.value,
      smokingPreference: smokingPreference.value,
      notes: notes.value
    }

  isSubmitting.value = true;

  try{
    const result = editingId.value === null
      ? await addCustomer(customerData)
      : await updateCustomer(editingId.value, customerData);

    if (result.success) {
      submitError.value = "";
      resetForm();
    } else {
      submitError.value = result.message;
    }
  }
    
  finally{
    isSubmitting.value = false;
  }
  
}



// 顧客情報の更新をキャンセル
function resetForm() {
  newName.value = "";
  newPhone.value = "";
  editingId.value = null;
  nameError.value = "";
  phoneError.value = "";
  notes.value = "";
  smokingPreference.value = "none";
}

// 宿泊登録をキャンセル
function cancelStay() {
  stayCustomerId.value = null;
}

const filteredCustomers = computed(() => {
  const query = searchQuery.value.trim();
  // console.log("customers :", customers.value);
  const filtered =  customers.value.filter(
    (customer) => customer.name.includes(query) || customer.phone.includes(query));

  if (sortBy.value === "count") {
      return [...filtered].sort((a,b) => b.stayCount - a.stayCount);
  } else {
    return [...filtered].sort((a,b) => new Date(b.lastStayedDate) - new Date(a.lastStayedDate));
  }
  });

function registerStay(customerId) {
  stayCustomerId.value = customerId;
  staySubmitError.value = "";
}

async function showStayHistory(customerId) {
  stayDeleteError.value = "";
  stayFetchError.value = "";
  stayHistory.value = [];
  historyCustomerId.value = null;

  const result = await fetchStays(customerId);
  if (result.success) {
    stayHistory.value = result.data;
    historyCustomerId.value = customerId;
  } else {
    stayFetchError.value = result.message; 
  }
}


function closeStayHistory() {
  stayDeleteError.value = "";
  historyCustomerId.value = null;
  stayHistory.value = [];
} 

async function handleDeleteStay(stayId) {
  const confirmed = window.confirm("この宿泊履歴を削除しますか？");
  if (!confirmed) return;
  
  stayDeleteError.value = "";
  stayFetchError.value = "";
  
  const result =  await deleteStay(stayId);
  if (result.success) {
    stayDeleteError.value = "";
    const stayResult = await fetchStays(historyCustomerId.value);
    if (stayResult.success) {
      stayHistory.value = stayResult.data;
    } else {
      stayFetchError.value = stayResult.message;
    }

  } else {
    stayDeleteError.value = result.message;
  }

}

async function handleDeleteCustomer(customerId) {
  const confirmed = window.confirm("この顧客情報を削除しますか？");
  if (!confirmed) return;

  const result = await deleteCustomer(customerId);
  if (result.success) {
    customerDeleteError.value = ""; 
  } else {
    customerDeleteError.value = result.message;
  }
}

async function handleStaySubmit(customerId, stayData) {
  isStaySubmitting.value = true;
  try {
    const result = await addStay(customerId, stayData);
  if (result.success) {
    staySubmitError.value = "";
    // フォームを閉じる
    cancelStay();
    
  } else {
    staySubmitError.value = result.message;
  }
  } finally {
    isStaySubmitting.value = false;
  }
  
}


</script>


  
<template>
  <main class="container">
    <h1>ホテル顧客管理台帳</h1>
    <div class="controls">
      <input class="search-input"
        v-model="searchQuery"
        type="text"
        placeholder="検索">

      <select class="sort-select" 
        v-model="sortBy">
        <option value="date">前回宿泊日が新しい順</option>
        <option value="count">宿泊回数が多い順</option>
      </select>
    </div>

    
    <StayHistory 
      v-if="historyCustomerId !== null"
      :stayHistory
      :stayDeleteError
      @delete-stay="handleDeleteStay"
      @close="closeStayHistory"
    />
    
    
    <CustomerList 
      :filtered-customers="filteredCustomers"
      :stay-customer-id="stayCustomerId"
      :is-stay-submitting="isStaySubmitting"
      :stay-submit-error="staySubmitError"
      @delete="handleDeleteCustomer"
      @edit="startEdit"
      @register-stay="registerStay"
      @show-history="showStayHistory"
      @cancel-stay="cancelStay"
      @add-stay="handleStaySubmit"/>
    <p v-if="customerDeleteError">{{ customerDeleteError }}</p>
    <p v-if="stayFetchError"> {{ stayFetchError }}</p>


  
    <h2>新規顧客登録</h2>

    <CustomerForm 
    :new-name="newName"
    :new-phone="newPhone"
    :editing-id="editingId"
    :name-error="nameError"
    :phone-error="phoneError"
    :smoking-preference="smokingPreference"
    :notes="notes"
    :is-submitting="isSubmitting"
    @update-name="newName=$event"
    @update-phone="newPhone=$event"
    @submit="handleSubmit"
    @clear-name-error="nameError=''"
    @clear-phone-error="phoneError=''"
    @cancel="resetForm"
    @update-smoking-preference="smokingPreference = $event"
    @update-notes="notes = $event"
    
    />
  </main>
  <p v-if="submitError">{{ submitError }}</p>
</template>



<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px;
}
.controls {
  display: flex;
  gap: 16px;
}

.search-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.sort-select {
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

@media (max-width: 600px) {
  .controls {
    flex-direction: column;
  }
}
</style>