$rg = 'AdirMelker-home-assignment'
New-AzResourceGroup -Name $rg -Location Eastus -Force

New-AzResourceGroupDeployment -ResourceGroupName $rg -TemplateFile 'storagesTemplate.json'

# Remove-AzResourceGroup -Name $rg -Force

# Remove-AzStorageAccount -Name 'storageaccountadir1' -Force


New-AzResourceGroupDeployment -ResourceGroupName $rg -TemplateFile 'vmtemplate.json' -TemplateParameterFile 'vmTemplate.parm.json'
