import site
site.addsitedir('lib')
import petty
print(petty.emiss(1,10.32,271.75,53.1))
print(petty.coef(271.75))
