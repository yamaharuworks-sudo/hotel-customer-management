<script setup>
import {ref, computed} from "vue";
import CustomerList from './components/CustomerList.vue'
import CustomerForm from "./components/CustomerForm.vue";
import { useCustomers } from "./composables/useCustomers.js";

const newName = ref("");
const newPhone = ref("");
const lastStayedDate = ref("");
const stayCount = ref(0);
const nameError = ref("");
const phoneError = ref("");
const editingId = ref(null);
const searchQuery = ref("");
const smokingPreference = ref("none");
const notes = ref("");

// 宿泊登録用
const stayCustomerId = ref(null);
const stayDate = ref("");
const stayNotes = ref("");

const sortBy = ref("date");

const {customers, addCustomer, deleteCustomer, updateCustomer, addStay} = useCustomers();


function startEdit(customer) {
  editingId.value = customer.id;
  newName.value = customer.name;
  newPhone.value = customer.phone;
  lastStayedDate.value = customer.lastStayedDate;
  stayCount.value = customer.stayCount;
  smokingPreference.value = customer.smokingPreference;
  notes.value = customer.notes;
}


function handleSubmit() {
  nameError.value = "";
  phoneError.value = "";

  let hasError = false;
  if (newName.value.trim() === "") {
    nameError.value = "氏名を入力してください";
    hasError = true;
  }
  if (newPhone.value.trim() === "") {
    phoneError.value = "電話番号を入力してください";
    hasError = true;
  }

  if (hasError) {
    return;
  } 
  const customerData = {
      name: newName.value,
      phone: newPhone.value,
      lastStayedDate: lastStayedDate.value,
      stayCount: stayCount.value,
      smokingPreference: smokingPreference.value,
      notes: notes.value
    }

  if (editingId.value === null) {
    addCustomer(customerData);
  } else {
    updateCustomer(editingId.value, customerData);
  }
  resetForm();
}

async function handleStaySubmit() {
  await addStay(stayCustomerId.value, {
    stayDate: stayDate.value,
    notes: stayNotes.value
  });
  stayDate.value = "";
  stayNotes.value = "";
  stayCustomerId.value = null;
}

function resetForm() {
  newName.value = "";
  newPhone.value = "";
  lastStayedDate.value = "";
  stayCount.value = 0;
  editingId.value = null;
  nameError.value = "";
  phoneError.value = "";
  notes.value = "";
  smokingPreference.value = "none";
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
  console.log(stayCustomerId.value);
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
    
    
    <CustomerList 
      :filtered-customers="filteredCustomers"
      @delete="deleteCustomer"
      @edit="startEdit"
      @register-stay="registerStay"/>

    <form @submit.prevent="handleStaySubmit" 
      v-if="stayCustomerId !== null">
      <input v-model="stayDate" type="date" >
      <textarea v-model="stayNotes"></textarea>
      <button type="submit">登録</button>
    </form> 

    <h2>新規顧客登録</h2>

    <CustomerForm 
    :new-name="newName"
    :new-phone="newPhone"
    :last-stayed-date="lastStayedDate"
    :stay-count="stayCount"
    :editing-id="editingId"
    :name-error="nameError"
    :phone-error="phoneError"
    :smoking-preference="smokingPreference"
    :notes="notes"
    @update-name="newName=$event"
    @update-phone="newPhone=$event"
    @update-last-stayed-date="lastStayedDate=$event"
    @update-stay-count="stayCount=$event"
    @submit="handleSubmit"
    @clear-name-error="nameError=''"
    @clear-phone-error="phoneError=''"
    @cancel="resetForm"
    @update-smoking-preference="smokingPreference = $event"
    @update-notes="notes = $event"/>
  </main>
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