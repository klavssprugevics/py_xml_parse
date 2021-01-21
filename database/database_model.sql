CREATE TABLE `Komanda` (
  `nosaukums` VARCHAR(45) NOT NULL,
  `punktu_sk` INT NOT NULL DEFAULT 0,
  `uzv_sk_pl` INT NOT NULL DEFAULT 0,
  `zaud_sk_pl` INT NOT NULL DEFAULT 0,
  `uzv_sk_pp` INT NOT NULL DEFAULT 0,
  `zaud_sk_pp` INT NOT NULL DEFAULT 0,
  `guto_vartu_sk` INT NOT NULL DEFAULT 0,
  `zaud_vartu_sk` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`nosaukums`));

CREATE TABLE `Speletajs` (
  `speletaja_nr` INT NOT NULL,
  `vards` VARCHAR(45) NOT NULL,
  `uzvards` VARCHAR(45) NOT NULL,
  `loma` VARCHAR(45) NOT NULL,
  `spelu_skaits` INT NOT NULL DEFAULT 0,
  `vartu_skaits` INT NOT NULL DEFAULT 0,
  `piespelu_skaits` INT NOT NULL DEFAULT 0,
  `sodu_skaits` INT NOT NULL DEFAULT 0,
  `komanda` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`speletaja_nr`),
  CONSTRAINT `fk_Speletajs_Komanda`
    FOREIGN KEY (`komanda`)
    REFERENCES `Komanda` (`nosaukums`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `Tiesnesis` (
  `tiesnesis_id` INTEGER PRIMARY KEY NOT NULL,
  `vards` VARCHAR(45) NOT NULL,
  `uzvards` VARCHAR(45) NOT NULL,
  `spelu_skaits` INT NOT NULL DEFAULT 0,
  `vt_skaits` INT NOT NULL DEFAULT 0);

CREATE TABLE `Speletaju_sastavs` (
  `speletaju_sastavs_id` INTEGER PRIMARY KEY NULL);

CREATE TABLE `Speletaji_sastava` (
  `speletajs` INT NOT NULL,
  `sastavs` INT NOT NULL,
  `pamatsastavs` TINYINT NOT NULL,
  PRIMARY KEY (`speletajs`, `sastavs`),
  CONSTRAINT `fk_Speletajs_has_Speletaju_saraksts_Speletajs1`
    FOREIGN KEY (`speletajs`)
    REFERENCES `Speletajs` (`speletaja_nr`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Speletajs_has_Speletaju_saraksts_Speletaju_saraksts1`
    FOREIGN KEY (`sastavs`)
    REFERENCES `Speletaju_sastavs` (`speletaju_sastavs_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `Spele` (
  `spele_id` INTEGER PRIMARY KEY NOT NULL,
  `datums` DATE NOT NULL,
  `vieta` VARCHAR(45) NOT NULL,
  `skatitaji` INT NOT NULL,
  `papildlaiks` TINYINT NULL,
  `komanda1` VARCHAR(45) NOT NULL,
  `sastavs1` INT NOT NULL,
  `varti1` INT NULL DEFAULT 0,
  `komanda2` VARCHAR(45) NOT NULL,
  `sastavs2` INT NOT NULL,
  `varti2` INT NULL DEFAULT 0,
  `vt` INT NOT NULL,
  `linijtiesnesis1` INT NOT NULL,
  `linijtiesnesis2` INT NOT NULL,
  CONSTRAINT `komanda1`
    FOREIGN KEY (`komanda1`)
    REFERENCES `Komanda` (`nosaukums`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `komanda2`
    FOREIGN KEY (`komanda2`)
    REFERENCES `Komanda` (`nosaukums`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `sastavs1`
    FOREIGN KEY (`sastavs1`)
    REFERENCES `Speletaju_sastavs` (`speletaju_sastavs_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `sastavs2`
    FOREIGN KEY (`sastavs2`)
    REFERENCES `Speletaju_sastavs` (`speletaju_sastavs_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `virstiesnesis`
    FOREIGN KEY (`vt`)
    REFERENCES `Tiesnesis` (`tiesnesis_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `linijtiesnesis1`
    FOREIGN KEY (`linijtiesnesis1`)
    REFERENCES `Tiesnesis` (`tiesnesis_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `linijtiesnesis2`
    FOREIGN KEY (`linijtiesnesis2`)
    REFERENCES `Tiesnesis` (`tiesnesis_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `Varti` (
  `varti_id` INTEGER PRIMARY KEY NOT NULL,
  `laiks` INT NOT NULL,
  `sitiens` VARCHAR(45) NOT NULL,
  `guvejs` INT NOT NULL,
  `piespele1` INT NULL,
  `piespele2` INT NULL,
  `piespele3` INT NULL,
  `spele` INT NOT NULL,
  CONSTRAINT `fk_Varti_Spele1`
    FOREIGN KEY (`spele`)
    REFERENCES `Spele` (`spele_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `guvejs`
    FOREIGN KEY (`guvejs`)
    REFERENCES `Speletajs` (`vards`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `piespele1`
    FOREIGN KEY (`piespele1`)
    REFERENCES `Speletajs` (`speletaja_nr`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `piespele2`
    FOREIGN KEY (`piespele2`)
    REFERENCES `Speletajs` (`speletaja_nr`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `piespele3`
    FOREIGN KEY (`piespele3`)
    REFERENCES `Speletajs` (`speletaja_nr`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);

CREATE TABLE `Sods` (
  `sods_id` INTEGER PRIMARY KEY NULL,
  `laiks` INT NOT NULL,
  `speletajs` INT NOT NULL,
  `spele` INT NOT NULL,
  CONSTRAINT `fk_Sods_Spele1`
    FOREIGN KEY (`spele`)
    REFERENCES `Spele` (`spele_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `speletajs`
    FOREIGN KEY (`speletajs`)
    REFERENCES `Speletajs` (`vards`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
