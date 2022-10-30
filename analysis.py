import json
import math
import os

import numpy as np
import scipy.stats
from matplotlib import pyplot as plt

import model.util.data_collectors as dc
from policies.run_settings import data_collectors, collector_groups, START_YEAR, END_YEAR

YEARS = range(START_YEAR, END_YEAR)

# TABLE_TARGET = "deckset"
TABLE_TARGET = "latex"


def distance_based_ks_test(mean_model_1, runs_model1, runs_model2):
    in_sample_distances = []

    for run1 in runs_model1:
        distance = np.sqrt(np.sum(np.square(mean_model_1 - run1)))
        in_sample_distances.append(distance)

    inter_sample_distances = []

    for run2 in runs_model2:
        distance = np.sqrt(np.sum(np.square(mean_model_1 - run2)))
        inter_sample_distances.append(distance)

    in_sample_distances = np.array(in_sample_distances)
    in_sample_distances = in_sample_distances[np.logical_not(np.isnan(in_sample_distances))]

    inter_sample_distances = np.array(inter_sample_distances)
    inter_sample_distances = inter_sample_distances[np.logical_not(np.isnan(inter_sample_distances))]

    if len(in_sample_distances) == 0 or len(inter_sample_distances) == 0:
        return 0

    pvalue = scipy.stats.mannwhitneyu(
        np.random.choice(in_sample_distances, min(len(in_sample_distances), 1000), replace=False),
        np.random.choice(inter_sample_distances, min(len(inter_sample_distances), 1000), replace=False),
        alternative='two-sided').pvalue

    # pvalue = scipy.stats.kstest(np.random.choice(in_sample_distances, 500, replace=False),
    #                             np.random.choice(inter_sample_distances, 500, replace=False)
    #                             ).pvalue

    # print(pvalue, pvalue < 0.05)
    return pvalue


def mean_based_higher_lower_test(mean_model1, model2):
    differences = []
    for run2 in model2:
        difference = np.sum(run2 - mean_model1)
        differences.append(difference)

    ratio = len([x for x in differences if x > 0]) / len(differences)
    if ratio <= 0.2:
        return "- -"
    elif ratio <= 0.4:
        return "-"
    elif ratio <= 0.6:
        return "?"
    elif ratio <= 0.8:
        return "+"
    else:
        return "++"


hypotheses = [
    {
        "name": "hypothesis1-export",
        "output_data_folder": "hypothesis1",
        "table_dc": [
            # (dc.mean_m2_per_person, ["-", "- -"], ["=", "?"]),
            # (dc.size_per_person_distribution, ["different"], []),
            # (dc.buy_price_prediction, ["-", "- -"], ["=", "?"]),
            # (dc.calculate_cost_of_living_rental, ["-", "- -"], ["=", "?"]),
            # # (dc.mean_private_sector_rent, ["-", "- -"], ["=", "="]),
            # (dc.count_homeless, ["-", "- -"], ["=", "?"]),
            # (dc.count_want_to_move, ["-", "- -"], ["=", "?"]),
            # (dc.actual_wait_time, ["-", "- -"], ["=", "?"]),
            # (dc.housing_shortage, ["-", "- -"], ["=", "?"]),
            # (dc.mean_utility, ["+", "++"], ["=", "?"]),
        ],
        "experiments": [
            {
                "name": "sharing",
                "models": [('base', 'base_model_fixed_construction.json'),
                           ('sharing', 'share_model.json')]
            },
            {
                "name": "splitting",
                "models": [('base', 'base_model_fixed_construction.json'),
                           ('splitting', 'splitting_model.json')]
            },
            {
                "name": "splitting-rewards",
                "models": [('splitting', 'splitting_model.json'),
                           # ('reward 5k', 'splitting_reward_model-reward=5000.json'),
                           ('10k reward', 'splitting_reward_model-reward=10000.json'),
                           ('20k reward', 'splitting_reward_model-reward=20000.json'),
                           ('30k reward', 'splitting_reward_model-reward=30000.json')]
            },
            # {
            #     "name": "sharing-rewards",
            #     "models": [('sharing', 'share_model.json'),
            #                ('reward 100', 'share_reward_model-reward=100.json'),
            #                ('reward 250', 'share_reward_model-reward=250.json'),
            #                ('reward 500', 'share_reward_model-reward=500.json')]
            # },
            {
                "name": "prohibit-too-high-m2-per-person",
                "models": [('base', 'base_model_fixed_construction.json'),
                           ('30 $m^2$ limit', 'm2_prohibit_model-m2_limit=30.json'),
                           ('55 $m^2$ limit', 'm2_prohibit_model-m2_limit=55.json'),
                           ('80 $m^2$ limit', 'm2_prohibit_model-m2_limit=80.json'),
                           ('105 $m^2$ limit', 'm2_prohibit_model-m2_limit=105.json')]
            },
            # {
            #     "name": "prohibit-m2-and-split",
            #     "models": [('base', 'base_model_fixed_construction.json'),
            #                ('m2 prohibit=30', 'm2_prohibit_and_split_model-m2_limit=30.json'),
            #                ('m2 prohibit=55', 'm2_prohibit_and_split_model-m2_limit=55.json'),
            #                ('m2 prohibit=80', 'm2_prohibit_and_split_model-m2_limit=80.json'),
            #                ('m2 prohibit=105', 'm2_prohibit_and_split_model-m2_limit=105.json')]
            # },
            {
                "name": "m2-per-person-tax",
                "models": [('base', 'base_model_fixed_construction.json'),
                           ('linear', 'm2_tax_model-policy=linear_tax_2.json'),
                           ('quadratic', 'm2_tax_model-policy=quadratic_tax.json'),
                           ('minimal needed space', 'm2_tax_model-policy=minimal_required_space.json'),
                           ]
            },
            # {
            #     "name": "share-m2-tax",
            #     "models": [('base', 'base_model_fixed_construction.json'),
            #                ('share m2 tax', 'share_m2_tax_model.json')]
            # },
            # {
            #     "name": "split-m2-tax",
            #     "models": [('base', 'base_model_fixed_construction.json'),
            #                ('split m2 tax', 'splitting_m2_tax_model.json')]
            # },
            {
                "name": "split-big-unused-buildings",
                "models": [('base', 'base_model_fixed_construction.json'),
                           # ('split > 30 m2 pp', 'split_unused_houses_model-split_limit=30.json'),
                           ('55 $m^2$ limit', 'split_unused_houses_model-split_limit=55.json'),
                           ('80 $m^2$ limit', 'split_unused_houses_model-split_limit=80.json'),
                           ('105 $m^2$ limit', 'split_unused_houses_model-split_limit=105.json')]
            },
            {
                "name": "base-model",
                "models": [('base', 'base_model_fixed_construction.json')]
            },
        ]
    }
]

test = [
    {
        "name": "hypothesis1",
        "table_dc": [
            (dc.mean_m2_per_person, ["-", "- -"], ["=", "?"]),
            (dc.size_per_person_distribution, ["different"], []),
            (dc.buy_price_prediction, ["-", "- -"], ["=", "?"]),
            (dc.calculate_cost_of_living_rental, ["-", "- -"], ["=", "?"]),
            # (dc.mean_private_sector_rent, ["-", "- -"], ["=", "="]),
            (dc.count_homeless, ["-", "- -"], ["=", "?"]),
            (dc.count_want_to_move, ["-", "- -"], ["=", "?"]),
            (dc.actual_wait_time, ["-", "- -"], ["=", "?"]),
            (dc.housing_shortage, ["-", "- -"], ["=", "?"]),
            (dc.mean_utility, ["+", "++"], ["=", "?"]),
        ],
        "experiments": [
            {
                "name": "sharing",
                "models": [('base', 'base_model_fixed_construction.json'),
                           ('sharing', 'share_model.json')]
            },
        ]
    }
]

for hypothesis in hypotheses:
    hypothesis_folder = "results/{}/".format(hypothesis["name"])
    if not os.path.exists(hypothesis_folder):
        os.makedirs(hypothesis_folder)

    for collector_group_name, _ in collector_groups:
        # group_folder = "results/{}/{}/".format(hypothesis["name"], collector_group_name)
        # if not os.path.exists(group_folder):
        #     os.makedirs(group_folder)

        for experiment in hypothesis["experiments"]:
            print("Start with: {}/{}/{}".format(hypothesis["name"], experiment["name"], collector_group_name))

            output_folder = "results/{}/{}/{}".format(hypothesis["name"], experiment["name"], collector_group_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            models = {}
            runs = {}

            for model_name, file_name in experiment["models"]:
                hypothesis_folder = hypothesis["output_data_folder"]
                with open('output_data/{}/{}'.format(hypothesis_folder, file_name)) as file:
                    model_data = json.load(file)

                    models[model_name] = {}
                    runs[model_name] = {}

                    # Collect data
                    for data_collector in data_collectors:
                        if data_collector.__chart_type__ == "hist":
                            models[model_name][data_collector.__name__] = {}

                            data_series = []

                            for run in model_data:
                                run_data = run[collector_group_name][data_collector.__name__][
                                    data_collector.__year__ - START_YEAR]
                                data_series.extend(run_data)

                            models[model_name][data_collector.__name__][data_collector.__year__] = data_series
                        else:
                            data_series = []

                            for run in model_data:
                                data = np.array(run[collector_group_name][data_collector.__name__])

                                if hasattr(data_collector, "__multiplier__"):
                                    data *= data_collector.__multiplier__

                                data_series.append(data)

                            runs[model_name][data_collector.__name__] = data_series
                            mean = np.nanmean(data_series, axis=0)
                            std_dev = np.std(data_series, axis=0)
                            models[model_name][data_collector.__name__] = mean, std_dev

            # Create graph
            for index, data_collector in enumerate(data_collectors):
                plt.rc('font', size=10)
                if data_collector.__chart_type__ == "bar" or data_collector.__chart_type__ == "hist":
                    fig_height = math.ceil(len(models) / 2) * 9
                    plt.figure(figsize=(20, fig_height)) # 15, fig_height
                    plt.rc('font', size=20)
                elif hasattr(data_collector, "__figsize__"):
                    plt.figure(figsize=data_collector.__figsize__)
                    plt.suptitle(data_collector.__title__)
                else:
                    plt.title(data_collector.__title__)

                min_ylim = 0
                max_ylim = 0.1
                max_xlim_hist = 0.1
                for i_model, model_name in enumerate(models):
                    if data_collector.__chart_type__ == "hist":
                        data = models[model_name][data_collector.__name__][data_collector.__year__]

                        max_xlim_hist = max(max_xlim_hist, np.max(data))

                        if len(models) > 1:
                            plt.subplot(math.ceil(len(models) / 2), 2, i_model + 1)
                        plt.title(model_name)

                        colors = ['#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
                                  '#7f7f7f', '#bcbd22', '#17becf']

                        n, bins, patches = plt.hist(data, bins=data_collector.__bins__)

                        plt.xlabel(data_collector.__xlabel__)
                        plt.ylabel(data_collector.__ylabel__)

                        # adapt the color of each patch
                        for c, p in zip(colors, patches):
                            p.set_facecolor(c)
                    else:
                        mean, std_dev = models[model_name][data_collector.__name__]

                        if data_collector.__chart_type__ == "bar":
                            if len(models) > 1:
                                plt.subplot(math.ceil(len(models) / 2), 2, i_model + 1)
                            plt.title(model_name)

                            max_ylim = max(max_ylim, np.max(np.sum(mean, axis=1)))

                            for i, label in enumerate(data_collector.bar_labels):
                                label_mean = mean[:, i]
                                label_std_dev = std_dev[:, i]

                                bottom = np.sum([mean[:, x] for x in range(i)], axis=0)
                                plt.bar(YEARS, label_mean, bottom=bottom, label=label)

                            plt.xlabel("Year")
                            plt.ylabel(data_collector.__ylabel__)
                            plt.legend()
                        elif data_collector.__chart_type__ == "line":
                            plt.plot(YEARS, mean, label=model_name)

                            if len(models) <= 3:
                                plt.fill_between(YEARS, mean + std_dev, mean - std_dev, alpha=0.3)

                            min_ylim = min(min_ylim, np.min(mean - 1.5 * std_dev))
                            max_ylim = max(max_ylim, np.max(mean + 1.5 * std_dev), np.max(mean * 1.1))

                            plt.ylim(min_ylim, max_ylim)
                            plt.xlim(START_YEAR, END_YEAR - 1)
                            plt.axhline(0, color="black", linewidth=0.3)
                            plt.xlabel("Year")
                            plt.ylabel(data_collector.__ylabel__)

                if data_collector.__chart_type__ == "bar":
                    for i_model, _ in enumerate(models):
                        if len(models) > 1:
                            plt.subplot(math.ceil(len(models) / 2), 2, i_model + 1)
                        plt.ylim(min_ylim, max_ylim * 1.05)
                elif data_collector.__chart_type__ == "hist":
                    max_y = 0
                    for i_model, _ in enumerate(models):
                        if len(models) > 1:
                            plt.subplot(math.ceil(len(models) / 2), 2, i_model + 1)
                        _, current_ymax = plt.ylim()

                        max_y = max(max_y, current_ymax)

                    for i_model, _ in enumerate(models):
                        if len(models) > 1:
                            plt.subplot(math.ceil(len(models) / 2), 2, i_model + 1)
                        plt.ylim(0, max_y)
                elif data_collector.__chart_type__ == "line":
                    plt.grid()

                if not data_collector.__chart_type__ == "hist":
                    plt.xticks([START_YEAR, 2020, 2030, 2040, 2050, 2060])
                    plt.legend()

                plt.savefig("results/{}/{}/{}/{}-{}.png".format(hypothesis["name"], experiment["name"],
                                                                collector_group_name, index, data_collector.__title__))
                plt.clf()
                plt.close()

            base_name = experiment["models"][0][0]
            print("base model name:", base_name)
            base_model = models[base_name]

            table = {
                'header': "||",
                'divider': "|---|"
            }

            continue

            for model_name in models:
                if model_name == base_name:
                    continue

                print("Processing:", model_name)

                table['header'] += "{}|".format(model_name)
                table['divider'] += "-|"

                model = models[model_name]

                for data_collector, green_expectations, orange_expectations in hypothesis["table_dc"]:
                    print(data_collector.__name__)
                    if data_collector.__name__ not in table:
                        table[data_collector.__name__] = "|{}|".format(data_collector.__title__)

                    status = ""
                    if data_collector.__chart_type__ == "hist":
                        base_distribution = np.random.choice(
                            base_model[data_collector.__name__][data_collector.__year__],
                            min(len(base_model[data_collector.__name__][data_collector.__year__]), 1000), replace=False)
                        model_distribution = np.random.choice(model[data_collector.__name__][data_collector.__year__],
                                                              min(len(model[data_collector.__name__][
                                                                          data_collector.__year__]), 1000),
                                                              replace=False)

                        # pvalue = scipy.stats.kstest(base_distribution, model_distribution).pvalue

                        pvalue = scipy.stats.mannwhitneyu(base_distribution, model_distribution,
                                                          alternative='two-sided').pvalue
                        status = "different" if pvalue < 0.05 else "similar"

                        # if status in green_expectations:
                        #     table[data_collector.__name__] += "<span style='color:green'>__{}__</span>|".format(status)
                        # elif status in orange_expectations:
                        #     table[data_collector.__name__] += "<span style='color:orange'>__{}__</span>|".format(status)
                        # else:
                        #     table[data_collector.__name__] += "<span style='color:red'>{}</span>|".format(status)
                    elif data_collector.__chart_type__ == "line":
                        base_data = base_model[data_collector.__name__][0]
                        model_data = model[data_collector.__name__][0]

                        # TODO: if we only calc from base to other model; we do not need to recalc in
                        #  sample distances each time as they are fixed!

                        mean, _ = models[base_name][data_collector.__name__]
                        p_value = distance_based_ks_test(
                            mean,
                            runs[base_name][data_collector.__name__],
                                                         runs[model_name][data_collector.__name__])

                        if p_value > 0.05:
                            status = "="
                        else:
                            status = mean_based_higher_lower_test(mean, runs[model_name][data_collector.__name__])

                    color = "red"
                    if status in green_expectations:
                        color = "green"
                    elif status in orange_expectations:
                        color = "orange"

                    if TABLE_TARGET == "deckset":
                        if color == "green":
                            table[data_collector.__name__] += "_{}_|".format(status)
                        elif color == "red":
                            table[data_collector.__name__] += "__{}__|".format(status)
                        else:
                            table[data_collector.__name__] += "{}|".format(status)
                    elif TABLE_TARGET == "latex":
                        color = "dark-" + color
                        table[data_collector.__name__] += "\\color{" + color + "}" + "__{}__|".format(status)
                    else:
                        table[data_collector.__name__] += "<span style='color:{}'>{}</span>|".format(color, status)

            with open("results/{}/{}/{}/table_{}.md".format(
                    hypothesis["name"], experiment["name"], collector_group_name, TABLE_TARGET), "w") as f:
                if TABLE_TARGET == "deckset":
                    f.write(
                        "[.text-emphasis: #006400, alignment(left|center|right), line-height(1), text-scale(1.0), Avenir Next Bold]\n"
                        "[.text-strong: #bb0000, alignment(left|center|right), line-height(1), text-scale(1.0), Avenir Next Bold]\n"
                        "[.text: Avenir Next Bold]\n"
                        )

                for line in table.values():
                    f.write(line + "\n")
                f.close()
