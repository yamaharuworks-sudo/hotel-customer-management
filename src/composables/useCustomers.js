import {ref, onMounted} from "vue";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


export function useCustomers() {


    async function fetchCustomers() {
        const response = await fetch(`${API_BASE_URL}/customers`);
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



    async function addCustomer(customerData) {
        try {
            const response = await fetch(`${API_BASE_URL}/customers`, {
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
            const response = await fetch(`${API_BASE_URL}/customers/${id}`, {
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
                    message: "サーバーに接続できません。ネットワーク接続を確認してください。"
            }
        }
        return {
                success: false,
                errorType: "server",
                message: "顧客を削除できませんでした。"
        }
        
    }

    async function deleteStay(stayId) {
        try {
            const response = await fetch(`${API_BASE_URL}/stays/${stayId}`, {
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
            const response = await fetch(`${API_BASE_URL}/customers/${id}`,{
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
            const response = await fetch(`${API_BASE_URL}/customers/${customerId}/stays`, 
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
            const response = await fetch(`${API_BASE_URL}/customers/${customerId}/stays`);
            
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
