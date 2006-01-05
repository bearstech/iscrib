# reload
all:
	@curl -s -u admin:a http://localhost:8080/Control_Panel/Products/ikaaro/manage_performRefresh | grep "Product refreshed"
	@curl -s -u admin:a http://localhost:8080/Control_Panel/Products/culture/manage_performRefresh | grep "Product refreshed"

clean:
	@find ./ -name "*.log" -exec rm -f {} \;
	@find ./ -name "*.out" -exec rm -f {} \;
	@find ./ -name "*.aux" -exec rm -f {} \;
	@find ./ -name "*.pyc" -exec rm -f {} \;
	@find ./gen -name "controlesBDP.py" -exec rm -f {} \;
	@find ./gen -name "controlesBM.py" -exec rm -f {} \;
	@find ./ -name "*_autogen*" -exec rm -f {} \;
	@rm -f *.bak
	@rm -f pot po bin
	@rm -f $(FR) $(MO)

# generate
PYTHON = $(shell python gen_all.py find_python)

gen_all: 
	$(PYTHON) gen_all.py gen_all

create_database: 
	$(PYTHON) gen_all.py create_database 

fill_tables: 
	$(PYTHON) gen_all.py fill_tables 

