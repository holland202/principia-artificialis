import numpy as np

# Strict seed for empirical tracking
np.random.seed(42)

# --- 1. SETUP MODEL ARCHITECTURE & SYNTHETIC DATA ---
# Inputs (d=4), Hidden (h=4), Output Classes (c=2) -> Total Params = (4*4) + (4*2) = 24
X = np.eye(4) 
# True targets for categorical cross-entropy gradient descent
Y_true = np.array([[1, 0], [0, 1], [1, 0], [0, 1]]) 

# Xavier-Normal Initialization
W1 = np.random.randn(4, 4) * np.sqrt(2.0 / 4)
W2 = np.random.randn(2, 4) * np.sqrt(2.0 / 4)

def forward_pass(w1, w2, x):
    """Computes hidden activations and softmax probability distributions."""
    h_act = w1 @ x.T # (4, 4)
    logits = w2 @ h_act # (2, 4)
    # Stable Softmax per sample
    exps = np.exp(logits - np.max(logits, axis=0, keepdims=True))
    probs = exps / np.sum(exps, axis=0, keepdims=True)
    return h_act.T, probs.T # Returns shapes (4,4) and (4,2)

def compute_exact_softmax_fim(w1, w2, x_data):
    """Builds an explicit 24x24 Fisher Information Matrix."""
    h_data, p_data = forward_pass(w1, w2, x_data)
    num_samples = x_data.shape[0]
    dim_total = (4 * 4) + (4 * 2) # 24
    fim = np.zeros((dim_total, dim_total))
    
    for i in range(num_samples):
        x = x_data[i:i+1, :] # (1, 4)
        h = h_data[i:i+1, :] # (1, 4)
        p = p_data[i, :]     # (2,)
        
        # Sample across possible output classes given the model's current distribution
        for target_class in range(2):
            prob_y = p[target_class]
            if prob_y < 1e-12: continue
            
            # Compute analytical gradients of log p(y|x) w.r.t W1 and W2
            d_logits = -p.copy()
            d_logits[target_class] += 1.0 # (2,)
            
            dW2 = np.outer(d_logits, h) # (2, 4)
            dh = d_logits @ w2          # (4,)
            dW1 = np.outer(dh, x)       # (4, 4)
            
            # Flatten and concatenate into a true 24-dimensional parameter gradient
            grad_vector = np.concatenate([dW1.flatten(), dW2.flatten()])
            
            # Accumulate expected value outer-product
            fim += prob_y * np.outer(grad_vector, grad_vector)
            
    return fim / num_samples

def run_gradient_descent_step(w1, w2, x_data, y_true, lr):
    """Executes a true cross-entropy gradient descent optimization step."""
    h_data, p_data = forward_pass(w1, w2, x_data)
    num_samples = x_data.shape[0]
    
    # Loss gradients
    d_logits = (p_data - y_true) / num_samples # (4, 2)
    dW2 = d_logits.T @ h_data # (2, 4)
    dh = d_logits @ w2 # (4, 4)
    dW1 = dh.T @ x_data # (4, 4)
    
    # Track cross-entropy loss
    loss = -np.sum(y_true * np.log(p_data + 1e-15)) / num_samples
    return w1 - lr * dW1, w2 - lr * dW2, loss

# --- 2. RUN EXPERIMENT AT LEARNING RATE = 0.1 ---
fim_0 = compute_exact_softmax_fim(W1, W2, X)
W1_1, W2_1, loss_0 = run_gradient_descent_step(W1, W2, X, Y_true, lr=0.1)
fim_1 = compute_exact_softmax_fim(W1_1, W2_1, X)

# Safely extract the non-zero eigenvalues to prevent rank-deficiency noise
def get_nonzero_eigenvalues(matrix):
    eigs = np.linalg.eigvalsh(matrix)
    return eigs[eigs > 1e-5] # Filter analytical null directions

eigs_0 = get_nonzero_eigenvalues(fim_0)
eigs_1 = get_nonzero_eigenvalues(fim_1)

subspace_cond_0 = np.max(eigs_0) / np.min(eigs_0)
subspace_cond_1 = np.max(eigs_1) / np.min(eigs_1)
empirical_ratio = subspace_cond_1 / subspace_cond_0

print(f"--- MATHEMATICALLY REDESIGNED RESULTS ---")
print(f"FIM Base Subspace Rank: {len(eigs_0)}")
print(f"Initial Cross-Entropy Loss: {loss_0:.4f}")
print(f"Isolated Subspace Ratio: {empirical_ratio:.4f}")
