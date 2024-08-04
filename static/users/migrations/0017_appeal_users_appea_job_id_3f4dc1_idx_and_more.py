# Generated by Django 5.0.7 on 2024-08-03 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0016_cv_word_experience'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='appeal',
            index=models.Index(fields=['job'], name='users_appea_job_id_3f4dc1_idx'),
        ),
        migrations.AddIndex(
            model_name='appeal',
            index=models.Index(fields=['owner'], name='users_appea_owner_i_6e5396_idx'),
        ),
        migrations.AddIndex(
            model_name='appeal',
            index=models.Index(fields=['whom'], name='users_appea_whom_id_a87967_idx'),
        ),
        migrations.AddIndex(
            model_name='appeal',
            index=models.Index(fields=['to'], name='users_appea_to_f8ee09_idx'),
        ),
        migrations.AddIndex(
            model_name='bankcard',
            index=models.Index(fields=['owner'], name='users_bankc_owner_i_c12aa3_idx'),
        ),
        migrations.AddIndex(
            model_name='bankcard',
            index=models.Index(fields=['card_number'], name='users_bankc_card_nu_7fa194_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['name'], name='users_categ_name_bcdc62_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['user_id'], name='users_custo_user_id_ab8992_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['phone_number'], name='users_custo_phone_n_f2d675_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['language'], name='users_custo_languag_c680a5_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['tg_username'], name='users_custo_tg_user_c06156_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['date_created'], name='users_custo_date_cr_ebf2e0_idx'),
        ),
        migrations.AddIndex(
            model_name='cv',
            index=models.Index(fields=['owner'], name='users_cv_owner_i_327929_idx'),
        ),
        migrations.AddIndex(
            model_name='cv',
            index=models.Index(fields=['rating'], name='users_cv_rating_bf372d_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['order'], name='users_job_order_i_9822b8_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['proposal'], name='users_job_proposa_6f71a2_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['status'], name='users_job_status_aa11a8_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['created_at'], name='users_job_created_c7852f_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['assignee'], name='users_job_assigne_45232d_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['owner'], name='users_order_owner_i_d6fbcb_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['category'], name='users_order_categor_b9acbe_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='users_order_status_52c9e5_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['created_at'], name='users_order_created_f5860d_idx'),
        ),
        migrations.AddIndex(
            model_name='passport',
            index=models.Index(fields=['owner'], name='users_passp_owner_i_d43fd7_idx'),
        ),
        migrations.AddIndex(
            model_name='passport',
            index=models.Index(fields=['series'], name='users_passp_series_642376_idx'),
        ),
        migrations.AddIndex(
            model_name='passport',
            index=models.Index(fields=['number'], name='users_passp_number_05fd21_idx'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['owner'], name='users_propo_owner_i_e85249_idx'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['order'], name='users_propo_order_i_4b1369_idx'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['status'], name='users_propo_status_ec332c_idx'),
        ),
        migrations.AddIndex(
            model_name='proposal',
            index=models.Index(fields=['created_at'], name='users_propo_created_0af9c6_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['job'], name='users_revie_job_id_2df8cc_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['owner'], name='users_revie_owner_i_19e665_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['whom'], name='users_revie_whom_id_fbf3bc_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['rating'], name='users_revie_rating_fdc639_idx'),
        ),
    ]
