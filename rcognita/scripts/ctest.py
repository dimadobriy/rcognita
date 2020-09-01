from rcognita import System, NominalController, Controller, Simulation
import argparse
import sys


def main(args=None):
    """main"""
    
    # environment
    sys = System() # already creates bot #1
    # sys.add_bots(-5,-5) # creates bot #2
    # sys.add_bots(-7,7) # creates bot #3

    agent1 = Controller(sys,
                        sample_time=0.3,
                        pred_step_size=0.6,
                        critic_mode=3,
                        ctrl_mode=3,
                        buffer_size=20,
                        n_actor=10,
                        n_critic=10,
                        t1=20,
                        estimator_update_time=0.3)

    # agent2 = Controller(sys,
    #                     sample_time=0.6,
    #                     pred_step_size=0.3,
    #                     critic_mode=3,
    #                     ctrl_mode=3,
    #                     buffer_size=20,
    #                     n_actor=10,
    #                     n_critic=10,
    #                     t1=18,
    #                     estimator_update_time=0.3)

    # agent3 = Controller(sys,
    #                     sample_time=0.6,
    #                     pred_step_size=0.3,
    #                     critic_mode=3,
    #                     ctrl_mode=3,
    #                     buffer_size=20,
    #                     n_actor=10,
    #                     n_critic=10,
    #                     t1=15,
    #                     estimator_update_time=0.3)

    nominal_ctrl = NominalController()
    # nominal_ctrl2 = NominalController()
    # nominal_ctrl3 = NominalController()

    sim = Simulation(sys, agent1, nominal_ctrl)
    # sim = Simulation(sys, [agent1, agent2, agent3], [nominal_ctrl, nominal_ctrl2, nominal_ctrl3])
    sim.run_simulation(n_runs=2, is_visualization=True, close_plt_on_finish=False, show_annotations=True, print_summary_stats=True, print_statistics_at_step=False)

if __name__ == "__main__":
    main()