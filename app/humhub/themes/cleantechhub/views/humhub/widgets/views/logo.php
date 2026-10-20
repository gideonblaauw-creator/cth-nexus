<?php
use humhub\components\View;
use yii\helpers\Url;

/** @var View $this */
?>
<a href="<?= Url::home(); ?>" class="navbar-brand logo-wrapper">
    <img src="<?= $this->theme->getBaseUrl(); ?>/resources/img/logo.png"
         alt="CleanTech Hub Nexus"
         style="max-height:44px; width:auto;" />
</a>
