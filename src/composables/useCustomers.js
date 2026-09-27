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
            stayCount: customer.stay_count,
            lastStayedDate: customer.last_stayed_date
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


    async function addCustomer(customerData) {

        const response = await fetch("http://127.0.0.1:8000/customers", {
            method: "POST", 
            headers: {
                "Content-Type": "application/json"
            }, 
            body: JSON.stringify({
                name: customerData.name,
                phone: customerData.phone,
                smoking_preference: customerData.smokingPreference,
                notes: customerData.notes
            })
        });
        if (response.ok) {
            await fetchCustomers();
        }
        
    }

    async function deleteCustomer(id) {
        const response = await fetch(`http://127.0.0.1:8000/customers/${id}`, {
            method: "DELETE"
        })
        if (response.ok) {
            await fetchCustomers();
        }
    }


    async function updateCustomer(id, customerData) {
        const response = await fetch(`http://127.0.0.1:8000/customers/${id}`,{
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: customerData.name,
                phone: customerData.phone,
                smoking_preference: customerData.smokingPreference,
                notes: customerData.notes
        })});
            if (response.ok) {
                await fetchCustomers();
            }
    }

    async function addStay(customerId, stayData) {
        const response = await fetch(`http://127.0.0.1:8000/customers/${customerId}/stays`, 
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    stay_date: stayData.stayDate,
                    notes: stayData.notes
                })
            }
        );
        if (response.ok){
            await fetchCustomers();    
        }
    }
        

    return {
        customers,
        addCustomer,
        deleteCustomer,
        updateCustomer,
        addStay
    };
}
