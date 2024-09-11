valid_objects = [
    'explore_groups', 'external_account_type_generic_groups', 'solution_template_generic_groups', 'external_account_types', 'solution_templates',
    'solutions', 'assistant_templates', 'assistants', 'threads', 'messages', 'runs', 'priorities', 'carts', 'orders', 'invoices', 'files', 'domains', 'messages', 'threads', 'demos', 'events', 'opportunities',
    'stripe_passports', 'users', 'meters', 'voting_topics', 'workflow_templates', 'invites'
]

objects_a = ['external_account_type_generic_groups_explore_groups', 'solution_template_generic_groups_explore_groups', 'users_stripe_passports']

objects_b = ['passports', 'solution_templates_workflow_templates']

context_map = {
    'passports': {'admin': {'tablename': "admin_stripe_passport", 'scope_objects': {'admin': {'tablename': "admins_stripe_passports", 'input': 'admin_id', 'output': "stripe_passport_id", 'output_relates_to': "admin_passport_id"}}},
                            'customer': {'tablename': "customer_stripe_passport", 'scope_objects': {'customer': {'tablename': "customers_stripe_passports", 'input': 'customer_id', 'output': "stripe_passport_id", 'output_relates_to': "customer_passport_id"}}},
                            'affiliate': {'tablename': "affiliate_stripe_passport", 'scope_objects': {'affiliate': {'tablename': "affiliates_stripe_passports", 'input': 'affiliate_id', 'output': "stripe_passport_id", 'output_relates_to': "affiliate_passport_id"}}}},
                
}