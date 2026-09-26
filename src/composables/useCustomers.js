import {ref, onMounted} from "vue";

export function useCustomers() {


    async function fetchCustomers() {
        const response = await fetch("http://127.0.0.1:8000/customers");
        const data = await response.json();
        customers.value = data.map((customer) => ({
            id: customer.id,
            name: customer.name,
            phone: customer.phone,
            smokingPreference: customer.smoking_preference,
            notes: customer.notes,
            stayCount: 0,
            lastStayedDate: ""
        }));

    }

    const customers = ref([]);


    onMounted(() => {
        fetchCustomers();
    });

    const customersId = customers.value.map((customer) => customer.id);
    let nextId = customersId.length === 0 
    ? 1
    : Math.max(...customersId) + 1;



    // customers が変更されたら自動で保存する watch
    // customersの値が変わったら、処理を実行
    // deep: trueでオブジェクト内の値の変更も検知
    // watch(customers, () => {
    // localStorage.setItem("customers", JSON.stringify(customers.value));

    // }, 
    // {
    //     deep: true
    // }
    // );


    function addCustomer(customerData) {

        const newCustomer = {
            id: nextId++,
            name: customerData.name,
            phone: customerData.phone,
            lastStayedDate: customerData.lastStayedDate,
            stayCount: customerData.stayCount,
            smokingPreference: customerData.smokingPreference,
            notes: customerData.notes
        };

        customers.value.push(newCustomer);
    }

    function deleteCustomer(id) {
        customers.value = customers.value.filter((customer) => customer.id !== id)
    }


    function updateCustomer(id, customerData) {
        const customer = customers.value.find(
            (customer) => customer.id === id
        )
        customer.name = customerData.name;
        customer.phone = customerData.phone;
        customer.lastStayedDate = customerData.lastStayedDate;
        customer.stayCount = customerData.stayCount;
        customer.smokingPreference = customerData.smokingPreference;
        customer.notes = customerData.notes;

    }

    return {
        customers,
        addCustomer,
        deleteCustomer,
        updateCustomer
    };
}