-- Migrate business operations to single column
-- First add the new column
ALTER TABLE companies ADD COLUMN business_operations TEXT;

-- Migrate existing data - build comma separated string for existing records
UPDATE companies 
SET business_operations = CONCAT_WS(', ',
    CASE WHEN Imports = 'Y' THEN 'imports' END,
    CASE WHEN Exports = 'Y' THEN 'exports' END,
    CASE WHEN Manufacture = 'Y' THEN 'manufacture' END,
    CASE WHEN Distribution = 'Y' THEN 'distribution' END,
    CASE WHEN Wholesale = 'Y' THEN 'wholesale' END,
    CASE WHEN Retail = 'Y' THEN 'retail' END,
    CASE WHEN Services = 'Y' THEN 'services' END,
    CASE WHEN Online = 'Y' THEN 'online' END,
    CASE WHEN Soft_Products = 'Y' THEN 'soft_products' END
);

-- Clean up empty strings (when no operations were selected)
UPDATE companies SET business_operations = NULL WHERE business_operations = '';

-- Now drop the old columns (uncomment after testing)
-- ALTER TABLE companies DROP COLUMN Imports;
-- ALTER TABLE companies DROP COLUMN Exports;
-- ALTER TABLE companies DROP COLUMN Manufacture;
-- ALTER TABLE companies DROP COLUMN Distribution;
-- ALTER TABLE companies DROP COLUMN Wholesale;
-- ALTER TABLE companies DROP COLUMN Retail;
-- ALTER TABLE companies DROP COLUMN Services;
-- ALTER TABLE companies DROP COLUMN Online;
-- ALTER TABLE companies DROP COLUMN Soft_Products;

-- Check results
SELECT record_id, company_group_print_name, business_operations 
FROM companies 
WHERE business_operations IS NOT NULL 
LIMIT 10;