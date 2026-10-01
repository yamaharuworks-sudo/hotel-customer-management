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
        try {
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
                return {
                    success: true,
                    errorType: null,
                    message: ""
                };
            }
        
        } catch (error) {
            console.error("顧客登録エラー", error);
            return {
                success: false,
                errorType: "network",
                message: "サーバーに接続できません。ネットワーク接続やサーバーPCの状態を確認し、改善しない場合は管理者にお問い合わせください。"
            };
        }
        return {
            success: false,
            errorType: "server",
            message: "保存できませんでした。管理者にお問い合わせください。"
        };
        
        
        
    }

    async function deleteCustomer(id) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/customers/${id}`, {
                method: "DELETE"
            })
            if (response.ok) {
                await fetchCustomers();
                return {
                    success: true,
                    errorType: null,
                    message: ""
                }
            }
        } catch (error) {
            console.log("顧客削除エラー", error);
            return {
                    success: false,
                    errorType: "network",
                    message: "顧客を削除できませんでした。管理者にお問い合わせください。"
            }
        }
        return {
                success: false,
                errorType: "server",
                message: "サーバーに接続できません。ネットワーク接続を確認してください。"
        }
        
    }

    async function deleteStay(stayId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/stays/${stayId}`, {
            method: "DELETE"
            })
            if (response.ok) {
                await fetchCustomers();
                return {
                    success: true,
                    errorType: null,
                    message: ""
                }
            }
        } catch (error) {
            console.log("宿泊履歴削除エラー", error);
            return {
                success: false,
                errorType: "network",
                message: "サーバーに接続できません。"
            };

        }
        return {    
            success: false,
            errorType: "server",
            message: "宿泊履歴を削除できませんでした。"
        };
        
        
    }


    async function updateCustomer(id, customerData) {
        try {
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
                return {
                    success: true,
                    errorType: null,
                    message: ""
                };
            }
        } catch (error) {
            console.error("顧客更新エラー", error);
            return {
                success: false,
                errorType: "network",
                message: "サーバーに接続できません。ネットワーク接続を確認し、改善しない場合は管理者にお問い合わせください。"
            };
        }
        return {
            success: false,
            errorType: "server",
            message: "更新できませんでした。管理者にお問い合わせください。"
        }
        
    }

    async function addStay(customerId, stayData) {
        try {
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
                return {
                    success: true,
                    errorType: null,
                    message: ""
                };
            }
        } catch(error) {
            console.log("宿泊登録エラー", error);
            return {
                success: false,
                errorType: "network",
                message: "サーバーに接続できません。ネットワーク接続を確認してください。"
            }

        }
        return {
            success: false,
            errorType: "server",
            message: "宿泊登録に失敗しました。管理者にお問い合わせください。"
        }
        
    }
    
    async function fetchStays(customerId) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/customers/${customerId}/stays`);
            
            if (response.ok) {
                const data = await response.json();
                return {
                    success: true,
                    errorType: null,
                    message: "",
                    data: data
                }
            }
        } catch(error) {
            console.log(error);
            return {
                success: false,
                errorType: "network",
                message: "サーバーに接続できません。",
                data: []
            }
        }
        return {
            success: false,
            errorType: "server",
            message: "宿泊履歴を取得できませんでした。",
            data: [] 
        }
    }
        

    return {
        customers,
        addCustomer,
        deleteCustomer,
        updateCustomer,
        addStay,
        fetchStays,
        deleteStay
    };
}
