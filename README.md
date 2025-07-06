<p align="center">
  <img src="https://img.utdstc.com/icon/55f/304/55f30479adbe539eb6a68aa776833c8bb2811e29deafcc1b8ab71e6862427eb9:200" alt="Gymrats Logo" width="120"/>
</p>

# Gymrats Dashboard

A Streamlit dashboard for visualizing and analyzing your personal training data from the **Gymrats App**.


---

## 🌐 Access

* **[Open the App](https://gymrats.streamlit.app/)**
  (Open the app directly from the link above — no installation needed!)

---

## 📦 Required Files

Upload the following CSV files exported from the Gymrats app:

* `account_check_ins.csv`
* `account_check_in_media.csv`
* `account_check_in_activities.csv` *(optional)*
* `challenge_check_ins.csv` *(optional)*
* `challenge_check_in_media.csv` *(optional)*
* `challenge_check_in_activities.csv` *(optional)*

---

## 📊 Features

* ✅ Upload your Gymrats-exported CSV files
* 📅 Daily workout tracking and trends
* 📈 Monthly and weekly summary metrics
* 🖼️ Workout photo wall
* 📤 Export detailed data table

---

## 🧾 Documentation

### 1. Dataset Descriptions

| CSV Name                            | Description                                     |
| ----------------------------------- | ----------------------------------------------- |
| `account_check_ins.csv`             | Main file with all your recorded workouts       |
| `account_check_in_media.csv`        | Links to photos uploaded during workouts        |
| `account_check_in_activities.csv`   | Raw data of activities per workout *(optional)* |
| `challenge_check_ins.csv`           | Check-ins from challenge workouts *(optional)*  |
| `challenge_check_in_media.csv`      | Photos from challenge workouts *(optional)*     |
| `challenge_check_in_activities.csv` | Activities from challenge workouts *(optional)* |

### 2. KPI Rules

### 📊 Indicator Documentation

| Indicator                | How it's Calculated                                | Technical Details                                                                 |
|--------------------------|----------------------------------------------------|------------------------------------------------------------------------------------|
| **% Year**               | Unique Active Days / Days since Jan 1st            | Counts unique `date` values since January 1st of the current year.                |
| **Avg Workouts/Week**    | Total check-ins / Weeks since Jan 1st              | Uses total days since Jan 1st ÷ 7 to calculate weeks passed.                      |
| **Avg Active Days/Week** | Unique check-in days / Weeks since Jan 1st         | Same denominator as above, but with unique active days in the numerator.          |
| **Monthly Active Days**  | Unique days with check-ins per month               | Aggregated per calendar month using normalized `date`.                            |
| **Month Days**           | Number of days with at least one check-in in month | Only counts dates where data is available, not full calendar days.                |
| **Missed Days**          | Month Days - Monthly Active Days                   | Indicates how many days had no activity despite available data.                   |
| **Most Missed Day**      | Weekday with lowest check-in frequency             | Computed from the distribution of `day_name`.                                     |
| **Most Frequent Hour**   | Most common hour of check-ins                      | Based on mode of `created_at.hour`.                                               |
| **Avg Time/Workout**     | Mean of workout durations                          | Uses numeric `duration` field, converted if needed.                               |
| **Avg Calories/Workout** | Mean of calories per workout                       | Calculated only if the `calorias` column is present.                              |


---

## 🙋‍♀️ About This Project

Made by [Tássia Giovanelli](https://www.linkedin.com/in/tassiagiovanelli/) to help Gymrats users track their workout journey with clarity, consistency and insights.

---

## 📮 Contribute

Feel free to open issues, suggest improvements or submit a PR if you'd like to contribute!
