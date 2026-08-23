import MDAnalysis as mda
import numpy as np
import time

def compute_and_save_order_parameters(tpr_file, traj_file, output_txt):
    print(f"Loading system from {tpr_file} and {traj_file}...")
    
    # 1. Load the Universe (topology + trajectory)
    u = mda.Universe(tpr_file, traj_file, refresh_offsets=True)
    
    # 2. Select the atoms that define the molecular vector
    # MDAnalysis automatically preserves the order of atoms as they appear in the topology
    c06_atoms = u.select_atoms("name C6")
    c10_atoms = u.select_atoms("name C10")
    
    n_molecules = len(c06_atoms)
    n_frames = len(u.trajectory)
    
    if len(c06_atoms) != len(c10_atoms):
        raise ValueError("Mismatch in number of C06 and C10 atoms! Check your topology names.")
        
    print(f"Found {n_molecules} molecules. Processing {n_frames} frames...")
    
    start_time = time.time()
    
    # 3. Open the output text file
    with open(output_txt, "w") as f:
        # Write a header for the text file
        f.write("Time_ps\tP1_Polar\tP2_Nematic\n")
        
        # 4. Iterate through the trajectory frame-by-frame
        for ts in u.trajectory:
            # Extract coordinates for the current frame
            pos_c06 = c06_atoms.positions
            pos_c10 = c10_atoms.positions
            
            # Calculate the raw vector
            vecs = pos_c10 - pos_c06
            
            # Apply Minimum Image Convention (Periodic Boundary Conditions)
            # This replicates the "while(dx < -Lx0*0.5) dx += Lx0" logic in your C++ code
            box = ts.dimensions[:3]  # Get box dimensions [Lx, Ly, Lz]
            vecs = vecs - box * np.round(vecs / box)
            
            # Normalize the vectors
            norms = np.linalg.norm(vecs, axis=1)[:, np.newaxis]
            norms[norms == 0] = 1.0  # Prevent division by zero
            u_vecs = vecs / norms
            
            # Construct the 3x3 Q-tensor
            Q = np.zeros((3, 3))
            Q[0, 0] = np.mean(1.5 * u_vecs[:, 0]**2 - 0.5)
            Q[0, 1] = np.mean(1.5 * u_vecs[:, 0] * u_vecs[:, 1])
            Q[0, 2] = np.mean(1.5 * u_vecs[:, 0] * u_vecs[:, 2])
            Q[1, 1] = np.mean(1.5 * u_vecs[:, 1]**2 - 0.5)
            Q[1, 2] = np.mean(1.5 * u_vecs[:, 1] * u_vecs[:, 2])
            Q[2, 2] = np.mean(1.5 * u_vecs[:, 2]**2 - 0.5)
            
            # Symmetrize the tensor
            Q[1, 0] = Q[0, 1]
            Q[2, 0] = Q[0, 2]
            Q[2, 1] = Q[1, 2]
            
            # Diagonalize the matrix
            eigenvalues, eigenvectors = np.linalg.eigh(Q)
            
            # Nematic order (P2) is the largest eigenvalue
            max_idx = np.argmax(eigenvalues)
            P2 = eigenvalues[max_idx]
            n_director = eigenvectors[:, max_idx]
            
            # Polar order (P1)
            p1_frame = np.mean(np.dot(u_vecs, n_director))
            P1 = np.abs(p1_frame)
            
            # Save the current time step data to the text file
            f.write(f"{ts.time:.2f}\t{P1:.6f}\t{P2:.6f}\n")
            
            # Optional: Print progress to the console every 1000 frames
            if ts.frame % 1000 == 0 and ts.frame > 0:
                print(f"Processed {ts.frame}/{n_frames} frames...")

    elapsed = time.time() - start_time
    print(f"\nFinished in {elapsed:.2f} seconds.")
    print(f"Results successfully saved to {output_txt}")

# --- Execute the script ---
if __name__ == "__main__":
    # Ensure these filenames match the actual files in your directory

    in_directory = r"Z:\polar_project\a_DIO\b_test1\4.2_P1ini0.5_T400"
    out_directory = r"D:\OneDrive\OneDrive2\OneDrive\polar_project\a_DIO\b_test1\4.2_P1ini0.5_T400\py"
    # in_directory = out_directory  # Use the same directory for input and output

    compute_and_save_order_parameters(
        tpr_file=in_directory + "\\npt_prod.tpr",
        traj_file=in_directory + "\\centered_prod.xtc",
        # traj_file=in_directory + "\\npt_prod.trr",
        output_txt=out_directory + "\\order_parameters_prod.txt"
    )