const cart = [];
let toastTimer;
document.addEventListener('DOMContentLoaded', () => {
  const year = document.getElementById('year'); if(year) year.textContent = new Date().getFullYear();
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === location.pathname.split('/').pop()) a.classList.add('active');
    a.addEventListener('click',()=>document.getElementById('navLinks')?.classList.remove('open'));
  });
  document.querySelectorAll('.sizes').forEach(group=>group.querySelectorAll('.size-btn').forEach(btn=>btn.addEventListener('click',()=>{
    group.querySelectorAll('.size-btn').forEach(b=>b.classList.remove('selected')); btn.classList.add('selected');
  })));
  document.querySelectorAll('.product .add-btn').forEach(btn=>btn.addEventListener('click',()=>addProduct(btn)));
  renderCart();
});

function showToast(message) {
  const t=document.getElementById('toast');
  if(!t)return;
  t.textContent=message;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>t.classList.remove('show'),2800)
}

function toggleMenu(){document.getElementById('navLinks')?.classList.toggle('open')}

function openNews(title, date, body) {
  document.getElementById('newsTitle').textContent = title;
  document.getElementById('newsDate').textContent = date;
  document.getElementById('newsBody').textContent = body;
  document.getElementById('newsBackdrop').classList.add('open');
  document.body.style.overflow='hidden';
}

function closeNews(){document.getElementById('newsBackdrop')?.classList.remove('open');document.body.style.overflow=''}

function openCart() {
  document.getElementById('cartBackdrop')?.classList.add('open');
  document.body.style.overflow='hidden';
  renderCart()
}

function closeCart(){document.getElementById('cartBackdrop')?.classList.remove('open');document.body.style.overflow=''}
function backdropClose(e,id){if(e.target.id===id){if(id==='newsBackdrop')closeNews();if(id==='cartBackdrop')closeCart()}}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeNews();closeCart()}})
function addProduct(button){const card=button.closest('.product');const name=card.dataset.product;const price=Number(card.dataset.price);const size=card.querySelector('.size-btn.selected')?.dataset.size||'M';const existing=cart.find(x=>x.name===name&&x.size===size);if(existing)existing.qty++;else cart.push({name,price,size,qty:1});renderCart();showToast(name+' (Size '+size+') added to cart.')}
function changeQty(index,change){if(!cart[index])return;cart[index].qty+=change;if(cart[index].qty<=0)cart.splice(index,1);renderCart()}

let productData = {
  detail: undefined,
  sizeType: undefined,
  priceOfOne: undefined,
  quantity: undefined
};

let products = [];

function renderCart() {
  const count=document.getElementById('cartCount');
  if(count)count.textContent=cart.reduce((s,x)=>s+x.qty,0);
  const holder = document.getElementById('cartItems');
  if(!holder)return;
  if(!cart.length)holder.innerHTML='<p class="muted">Your cart is empty. Add a jersey to get started.</p>';
  else holder.innerHTML=cart.map((x,i)=>`<div class="cart-row"><div><strong>${escapeHTML(x.name)}</strong><div class="muted">Size ${escapeHTML(x.size)} · KES ${x.price.toLocaleString()} each</div></div><div class="qty"><button onclick="changeQty(${i},-1)">−</button><strong>${x.qty}</strong><button onclick="changeQty(${i},1)">+</button></div></div>`).join('');
  
  cart.map((x,i) => {
     productData.detail = escapeHTML(x.name);
     productData.sizeType = escapeHTML(x.size);
     productData.priceOfOne = x.price.toLocaleString();
     productData.quantity = x.qty;
     
     products.push(productData);
  });
 

  const total=document.getElementById('cartTotal');
  if(total)total.textContent='KES '+cart.reduce((s,x)=>s+x.price*x.qty,0).toLocaleString()
}

function escapeHTML(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

function checkoutDemo() {
  if(!cart.length)
    {
      showToast('Your cart is empty.');
      return;
    }
    //showToast('Demo checkout only. Connect a secure backend and payment provider before accepting payments.')

  //let phone_number = document.getElementById('phone_number').value.trim()
  let amount = document.getElementById('cartTotal').innerText;
  let product_details = document.getElementById('')

  
  function extractAmount(str) {
  // Match optional sign, digits, optional commas, optional decimal part
  const match = String(str).replace(/,/g, "").match(/-?\d+(\.\d+)?/);
  return match ? parseFloat(match[0]) : null;
}

  try {
    /**
 * Normalize a Kenyan phone number to the format: 2547XXXXXXXX or 2541XXXXXXXX
 * Accepts:
 *   +254712345678
 *   254712345678
 *   0712345678
 *   0112345678
 *   712345678
 *   112345678
 * Returns:
 *   "254712345678" if valid, otherwise null
 */
function normalizeKenyanPhone(input) {
  if (typeof input !== "string") return null;

  // Remove spaces, hyphens, parentheses, and dots
  let phone = input.replace(/[\s\-().]/g, "");

  // Normalize country code / leading zero
  if (phone.startsWith("+254")) {
    phone = phone.slice(1); // +254... -> 254...
  } else if (phone.startsWith("254")) {
    // already 254...
  } else if (phone.startsWith("0")) {
    phone = "254" + phone.slice(1); // 07... -> 2547..., 01... -> 2541...
  } else if (/^[71]\d{8}$/.test(phone)) {
    phone = "254" + phone; // 7XXXXXXXX or 1XXXXXXXX -> 254...
  } else {
    return null;
  }

  // Kenyan mobile numbers: 254 followed by 7 or 1, then 8 digits
  if (!/^254(7|1)\d{8}$/.test(phone)) {
    return null;
  }

  return phone;
}

/**
 * Check if a Kenyan phone number is valid.
 */
function isValidKenyanPhone(input) {
  return normalizeKenyanPhone(input) !== null;
}
/*
// Examples
console.log(isValidKenyanPhone("+254712345678")); // true
console.log(isValidKenyanPhone("254712345678"));  // true
console.log(isValidKenyanPhone("0712345678"));    // true
console.log(isValidKenyanPhone("0112345678"));    // true
console.log(isValidKenyanPhone("712345678"));     // true
console.log(isValidKenyanPhone("112345678"));     // true

console.log(isValidKenyanPhone("0812345678"));    // false
console.log(isValidKenyanPhone("071234567"));     // false
console.log(isValidKenyanPhone("+254812345678")); // false

console.log(normalizeKenyanPhone("0712 345 678")); // "254712345678"
*/

if (isValidKenyanPhone(phone_number)) {
  //document.getElementById('phone_error').innerText = "";

} else throw new SyntaxError();
  } catch(error) {
    //document.getElementById('phone_error').innerText = "Invalid Phone Number!";
    return;
  }
  const csrftoken = document.getElementById('csrf').innerText;

  function getCSRFToken() {
    return csrftoken;//document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
console.log(JSON.stringify(products)); window.location.href = `/proceedNpay/`; return;
  fetch('/save-json/',{
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify(products)
})
.then(res => res.json())
.then(data => console.log("Saved!",data));

  //window.location.href = `/proceedNpay/`;
  return;
  async function sendData() {
    try {
        const response = await fetch(`/pay/${normalizeKenyanPhone(phone_number)}/${extractAmount(amount)}`, {
            method: 'GET',
            //credentials: 'same-origin', // Include cookies for CSRF
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken , // Attach the CSRF token
                //'X-Requested-With': 'XMLHttpRequest', // Optional: helps Django identify AJAX
            },
            //body: JSON.stringify({ "phone_number": normalizeKenyanPhone(phone_number), "amount": extractAmount(amount) }), // Convert JavaScript object to JSON string*/
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        alert(result);
    } catch (error) {
        console.error('Error:', error);
    }
  } //sendData();
}


function submitDemoForm(e){e.preventDefault();showToast('Thanks! This demo form is not connected to email yet.');e.target.reset()}

