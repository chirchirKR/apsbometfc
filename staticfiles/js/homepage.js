const cart = [];
let toastTimer;
document.getElementById('year').textContent = new Date().getFullYear();

function showToast(message){
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=>toast.classList.remove('show'),2800);
}
function toggleMenu(){document.getElementById('navLinks').classList.toggle('open')}
document.querySelectorAll('.nav-links a').forEach(link=>link.addEventListener('click',()=>{
  document.getElementById('navLinks').classList.remove('open');
  document.querySelectorAll('.nav-links a').forEach(a=>a.classList.remove('active'));
  link.classList.add('active');
}));
document.querySelectorAll('.sizes').forEach(group=>{
  group.querySelectorAll('.size-btn').forEach(btn=>btn.addEventListener('click',()=>{
    group.querySelectorAll('.size-btn').forEach(b=>b.classList.remove('selected'));
    btn.classList.add('selected');
  }));
});
function addProduct(button){
  const card = button.closest('.product');
  const name = card.dataset.product;
  const price = Number(card.dataset.price);
  const selected = card.querySelector('.size-btn.selected');
  const size = selected ? selected.dataset.size : 'M';
  const existing = cart.find(item=>item.name===name && item.size===size);
  if(existing) existing.qty++;
  else cart.push({name,price,size,qty:1});
  renderCart();
  showToast(name+' (Size '+size+') added to cart.');
}
function renderCart(){
  const count = cart.reduce((sum,item)=>sum+item.qty,0);
  document.getElementById('cartCount').textContent = count;
  const holder = document.getElementById('cartItems');
  if(!cart.length){
    holder.innerHTML='<div class="empty-cart">Your cart is empty.<br>Choose a jersey to get started.</div>';
  } else {
    holder.innerHTML = cart.map((item,index)=>`
      <div class="cart-item">
        <div><strong>${escapeHTML(item.name)}</strong><small>Size ${escapeHTML(item.size)} · KES ${item.price.toLocaleString()} each</small></div>
        <div class="qty-controls">
          <button aria-label="Decrease quantity" onclick="changeQty(${index},-1)">−</button><strong>${item.qty}</strong>
          <button aria-label="Increase quantity" onclick="changeQty(${index},1)">+</button>
        </div>
      </div>`).join('');
  }
  const total=cart.reduce((sum,item)=>sum+item.price*item.qty,0);
  document.getElementById('cartTotal').textContent='KES '+total.toLocaleString();
}
function escapeHTML(value){return String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]))}
function changeQty(index,change){
  if(!cart[index])return;
  cart[index].qty+=change;
  if(cart[index].qty<=0)cart.splice(index,1);
  renderCart();
}
function openCart(){
  document.getElementById('cartBackdrop').classList.add('open');
  document.body.style.overflow='hidden';
  renderCart();
}
function closeCart(){
  document.getElementById('cartBackdrop').classList.remove('open');
  document.body.style.overflow='';
}
function backdropClose(event){if(event.target.id==='cartBackdrop')closeCart()}
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeCart()});
function checkoutDemo(){
  if(!cart.length){showToast('Your cart is empty.');return}
  showToast('Demo checkout only. Connect a backend and payment provider to accept payments.');
}
renderCart();