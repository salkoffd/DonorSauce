CREATE TABLE donors
(
	name character varying(50) PRIMARY KEY,
	total int,
	count int
)

CREATE TABLE legislators
(
	bioguide character varying(50) PRIMARY KEY,
	id character varying(50) UNIQUE,
	first_name character varying(50),
	last_name character varying(50),
	birthday character varying(50),
	gender character varying(10),
	religion character varying(50),
	address character varying(100),
	district character varying(50),
	party character varying(50),
	phone character varying(50),
	state character varying(10),
	leg_type character varying(10),
	url character varying(100),
	latitude numeric,
	longitude numeric,
	age int
)

CREATE TABLE donations
(
	donation_number int PRIMARY KEY,
	donor character varying(50),
	legislator character varying(50),
	amount int,
	releasedate character varying(100),
	FOREIGN KEY (donor) REFERENCES donors (name),
	FOREIGN KEY (legislator) REFERENCES legislators (id)
)

-- SELECT donors.name, donations.amount FROM legislators, donors, donations
--     WHERE legislators.id = donations.legislator AND donors.name = donations.donor AND
--     legislators.first_name = 'Bernard' AND legislators.last_name = 'Sanders'
--     ORDER BY donations.amount desc


    