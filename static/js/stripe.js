// Get Stripe publishable key
fetch("/config/")
    .then((result) => { return result.json(); })
    .then((data) => {
        // Initialize Stripe.js
        const stripe = Stripe(data.publicKey);

        // Event handler
        let submitBtn = document.querySelector("#checkout");
        if (submitBtn !== null) {
            submitBtn.addEventListener("click", () => {
                // Get Checkout Session ID
                fetch("/create-checkout-session/")
                    .then((result) => { return result.json(); })
                    .then((data) => {
                        console.log(data);
                        // Redirect to Stripe Checkout
                        return stripe.redirectToCheckout({ sessionId: data.sessionId })
                    })
                    .then((res) => {
                        console.log(res);
                    });
            });
        }
    });

    document.addEventListener("DOMContentLoaded", function() {
        const stripe = Stripe('pk_test_51PyCjbDDYJcRPnIUQOk8J2BIOrWfaWq5YaKl80rmRW8ZLA8MkngSsKxgJuhHYGCuVZfQYIrNxPCqqu3HXhFuK87C00wWxgm0hf');
        const elements = stripe.elements();
        
        const cardElement = elements.create('card');
        cardElement.mount('#card-element');
        
        document.getElementById('payment-form').addEventListener('submit', function(event) {
            event.preventDefault();
    
            stripe.createPaymentMethod({
                type: 'card',
                card: cardElement,
            }).then(function(result) {
                if (result.error) {
                    console.error(result.error);
                    alert('エラー: ' + result.error.message);
                } else {
                    const newPaymentMethodId = result.paymentMethod.id;
                    const subscriptionId = document.getElementById('subscriptionId').value;
                    const oldPaymentMethodId = document.getElementById('StripeSubscriptionId').value;
    
                    fetch('/update_payment_method/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            payment_method_id: newPaymentMethodId,
                            old_payment_method_id: oldPaymentMethodId,
                            subscription_id: subscriptionId
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // 更新が成功した場合、リダイレクト
                            window.location.href = '/update_payment_method_success/';
                        } else {
                            alert('支払い方法の更新中にエラーが発生しました: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('エラー:', error);
                    });
                }
            });
        });
    });