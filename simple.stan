data {
  int<lower=0> n_countries;
  int<lower=0> n_data; // number of time series data points

  // deaths are cumulative
  int deaths[n_countries, n_data];
  int confirmed[n_countries, n_data];
  row_vector[n_countries] vulnerable_pop;
  row_vector[n_countries] total_pop;
}
transformed data {
  row_vector[n_countries] log_vulnerable_pop;
  row_vector[n_countries] log_total_pop;
  
  log_vulnerable_pop = log(vulnerable_pop);
  log_total_pop = log(total_pop);
}
parameters {
  // mortality relative to previous study
  real log_rel_mortality;
  
  // unknown: fraction of population infected
  matrix<lower=-20, upper=0>[n_countries, n_data] log_frac_infected;
 
  // fraction of reported confirmed cases out of infected 
  // (due to biases, aggressiveness in testing, underreporting)
  row_vector<lower=-20, upper=5>[n_countries] log_frac_discovered;
}
model {
  log_rel_mortality ~ normal(0, 1);
  
  // we assume the deaths have already been time shifted or are instantineous
  // and are a fraction of the population
  for (i in 1:n_countries) {
     deaths[i] ~ poisson_log(log_vulnerable_pop[i] + log_frac_infected[i] + log_rel_mortality);

     // the number of confirmed cases:
     confirmed[i] ~ poisson_log(log_total_pop[i] + log_frac_infected[i] + log_frac_discovered[i]);
  }
}
