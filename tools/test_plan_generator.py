# tasks/test_plan_generator.py
def create_test_plan(client, feature):
    prompt = f"Create a concise QA test plan for the feature: {feature}. Include test objectives, scenarios, and data points."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a QA test planner."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
